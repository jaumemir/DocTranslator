# translate/md.py
"""
Markdown file translation processor
Chunking strategy:
1. Protect code blocks, inline code, formulas, HTML tag structures
2. Split by semantic blocks (headings, lists, quotes, tables, paragraphs)
3. Maintain block integrity
4. Split oversized blocks at sentence boundaries
5. Preserve links/images without translation
"""

import re
import datetime
import logging
from threading import Event
from typing import List, Dict, Tuple
from dataclasses import dataclass
from . import to_translate
from . import common

# Chunking configuration
MAX_CHUNK_SIZE = 2000


@dataclass
class ProtectedBlock:
    """Protected block (not translated)"""
    placeholder: str
    content: str
    block_type: str  # code_block, inline_code, formula, html_tag, link, image


def start(trans: Dict) -> bool:
    """
    Markdown file translation entry point
    :param trans: Translation configuration dictionary
    :return: Whether successful
    """
    translate_id = trans['id']
    start_time = datetime.datetime.now()

    # Read file
    try:
        with open(trans['file_path'], 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(trans['file_path'], 'r', encoding='gbk') as f:
                content = f.read()
        except Exception as e:
            logging.error(f"[Task {translate_id}] Failed to read file: {e}")
            to_translate.error(translate_id, f"Failed to read file: {str(e)}")
            return False
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to read file: {e}")
        to_translate.error(translate_id, f"Failed to read file: {str(e)}")
        return False

    if not content or not content.strip():
        logging.info(f"[Task {translate_id}] File content is empty")
        with open(trans['target_file'], 'w', encoding='utf-8') as f:
            f.write("")
        to_translate.complete(trans, 0, "0s")
        return True

    # Preprocess: protect special syntax
    processed_content, protected_blocks = _protect_special_syntax(content)

    # Smart chunking
    texts = _smart_chunk_markdown(processed_content)

    # Count blocks that need translation
    to_translate_count = sum(1 for t in texts if not t.get('skip', False))

    if to_translate_count == 0:
        logging.info(f"[Task {translate_id}] No content to translate")
        with open(trans['target_file'], 'w', encoding='utf-8') as f:
            f.write(content)
        to_translate.complete(trans, 0, "0s")
        return True

    logging.info(
        f"[Task {translate_id}] Split into {len(texts)} blocks, {to_translate_count} need translation")

    # Execute translation
    event = Event()
    success = to_translate.translate_batch(trans, texts, event)
    if not success:
        return False

    # Rebuild document and write results
    try:
        text_count = _write_result(trans, texts, protected_blocks)
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to write file: {e}")
        to_translate.error(translate_id, f"Failed to write file: {str(e)}")
        return False

    end_time = datetime.datetime.now()
    spend_time = common.display_spend(start_time, end_time)
    to_translate.complete(trans, text_count, spend_time)
    return True


def _protect_special_syntax(content: str) -> Tuple[str, List[ProtectedBlock]]:
    """
    Preprocessing: replace special syntax that doesn't need translation with placeholders
    :return: (processed content, list of protected blocks)
    """
    protected_blocks = []
    placeholder_counter = [0]

    def make_placeholder(block_type: str) -> str:
        placeholder_counter[0] += 1
        return f"⟦{block_type.upper()}_{placeholder_counter[0]}⟧"

    def protect(match, block_type: str) -> str:
        placeholder = make_placeholder(block_type)
        protected_blocks.append(ProtectedBlock(
            placeholder=placeholder,
            content=match.group(0),
            block_type=block_type
        ))
        return placeholder

    # 1. Protect code blocks ```...``` (must process first to avoid internal content matching other rules)
    content = re.sub(
        r'```[\s\S]*?```',
        lambda m: protect(m, 'code_block'),
        content
    )

    # 2. Protect inline code `...`
    content = re.sub(
        r'`[^`\n]+`',
        lambda m: protect(m, 'inline_code'),
        content
    )

    # 3. Protect LaTeX formula blocks $$...$$
    content = re.sub(
        r'\$\$[\s\S]*?\$\$',
        lambda m: protect(m, 'formula_block'),
        content
    )

    # 4. Protect inline formulas $...$
    content = re.sub(
        r'\$[^\$\n]+\$',
        lambda m: protect(m, 'formula_inline'),
        content
    )

    # 5. Protect images ![alt](url) or ![alt](url "title")
    content = re.sub(
        r'!\[[^\]]*\]\([^)]+\)',
        lambda m: protect(m, 'image'),
        content
    )

    # 6. Protect link URL part, but keep display text
    # [display text](url) -> [display text](⟦LINK_URL_X⟧)
    def protect_link(match):
        full_match = match.group(0)
        text = match.group(1)  # Display text
        url = match.group(2)  # URL part

        # Only protect URL part
        url_placeholder = make_placeholder('link_url')
        protected_blocks.append(ProtectedBlock(
            placeholder=url_placeholder,
            content=f"]({url})",
            block_type='link_url'
        ))
        return f"[{text}{url_placeholder}"

    content = re.sub(
        r'\[([^\]]+)\](\([^)]+\))',
        protect_link,
        content
    )

    # 7. Protect HTML tags (keep tag structure, internal text will be translated)
    # Only protect self-closing tags and pure tags (no content)
    content = re.sub(
        r'<[^>]+/>',
        lambda m: protect(m, 'html_self_closing'),
        content
    )

    # Protect HTML comments
    content = re.sub(
        r'<!--[\s\S]*?-->',
        lambda m: protect(m, 'html_comment'),
        content
    )

    return content, protected_blocks


def _smart_chunk_markdown(content: str) -> List[Dict]:
    """
    Smart chunking of Markdown content
    Split by semantic blocks: headings, lists, quotes, tables, paragraphs
    """
    texts = []

    # Normalize line breaks
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Process line by line
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i]

        # Empty line - use as separator
        if not line.strip():
            texts.append(_make_text_item('', skip=True, block_type='separator'))
            i += 1
            continue

        # Horizontal rule (---, ***, ___)
        if re.match(r'^[\-\*_]{3,}\s*$', line.strip()):
            texts.append(_make_text_item(line, skip=True, block_type='hr'))
            i += 1
            continue

        # Heading (# ## ### etc.)
        if re.match(r'^#{1,6}\s+', line):
            # Check if heading content needs translation
            header_match = re.match(r'^(#{1,6}\s+)(.*)$', line)
            if header_match:
                prefix = header_match.group(1)
                title_text = header_match.group(2)
                if _should_translate(title_text):
                    texts.append(_make_text_item(
                        line,
                        block_type='header',
                        prefix=prefix,
                        content_text=title_text
                    ))
                else:
                    texts.append(_make_text_item(line, skip=True, block_type='header'))
            i += 1
            continue

        # Table (starts with |)
        if line.strip().startswith('|'):
            table_lines, end_i = _collect_table(lines, i)
            table_text = '\n'.join(table_lines)
            if _should_translate(table_text):
                if len(table_text) > MAX_CHUNK_SIZE:
                    # Table too large, split by rows
                    sub_chunks = _split_table(table_lines)
                    for j, chunk in enumerate(sub_chunks):
                        texts.append(_make_text_item(
                            chunk,
                            block_type='table',
                            is_sub=True,
                            sub_index=j,
                            sub_total=len(sub_chunks)
                        ))
                else:
                    texts.append(_make_text_item(table_text, block_type='table'))
            else:
                texts.append(_make_text_item(table_text, skip=True, block_type='table'))
            i = end_i
            continue

        # Quote block (starts with >)
        if line.strip().startswith('>'):
            quote_lines, end_i = _collect_quote(lines, i)
            quote_text = '\n'.join(quote_lines)
            if _should_translate(quote_text):
                if len(quote_text) > MAX_CHUNK_SIZE:
                    sub_chunks = _split_quote(quote_lines)
                    for j, chunk in enumerate(sub_chunks):
                        texts.append(_make_text_item(
                            chunk,
                            block_type='quote',
                            is_sub=True,
                            sub_index=j,
                            sub_total=len(sub_chunks)
                        ))
                else:
                    texts.append(_make_text_item(quote_text, block_type='quote'))
            else:
                texts.append(_make_text_item(quote_text, skip=True, block_type='quote'))
            i = end_i
            continue

        # Unordered list (starts with - * +)
        if re.match(r'^[\s]*[-\*\+]\s+', line):
            list_lines, end_i = _collect_list(lines, i, 'unordered')
            list_text = '\n'.join(list_lines)
            if _should_translate(list_text):
                if len(list_text) > MAX_CHUNK_SIZE:
                    sub_chunks = _split_list(list_lines)
                    for j, chunk in enumerate(sub_chunks):
                        texts.append(_make_text_item(
                            chunk,
                            block_type='list',
                            is_sub=True,
                            sub_index=j,
                            sub_total=len(sub_chunks)
                        ))
                else:
                    texts.append(_make_text_item(list_text, block_type='list'))
            else:
                texts.append(_make_text_item(list_text, skip=True, block_type='list'))
            i = end_i
            continue

        # Ordered list (starts with number.)
        if re.match(r'^[\s]*\d+\.\s+', line):
            list_lines, end_i = _collect_list(lines, i, 'ordered')
            list_text = '\n'.join(list_lines)
            if _should_translate(list_text):
                if len(list_text) > MAX_CHUNK_SIZE:
                    sub_chunks = _split_list(list_lines)
                    for j, chunk in enumerate(sub_chunks):
                        texts.append(_make_text_item(
                            chunk,
                            block_type='list',
                            is_sub=True,
                            sub_index=j,
                            sub_total=len(sub_chunks)
                        ))
                else:
                    texts.append(_make_text_item(list_text, block_type='list'))
            else:
                texts.append(_make_text_item(list_text, skip=True, block_type='list'))
            i = end_i
            continue

        # Regular paragraph (consecutive non-empty lines)
        para_lines, end_i = _collect_paragraph(lines, i)
        para_text = '\n'.join(para_lines)
        if _should_translate(para_text):
            if len(para_text) > MAX_CHUNK_SIZE:
                sub_chunks = _split_by_sentences_md(para_text)
                for j, chunk in enumerate(sub_chunks):
                    texts.append(_make_text_item(
                        chunk,
                        block_type='paragraph',
                        is_sub=True,
                        sub_index=j,
                        sub_total=len(sub_chunks)
                    ))
            else:
                texts.append(_make_text_item(para_text, block_type='paragraph'))
        else:
            texts.append(_make_text_item(para_text, skip=True, block_type='paragraph'))
        i = end_i

    return texts


def _collect_table(lines: List[str], start: int) -> Tuple[List[str], int]:
    """Collect table rows"""
    table_lines = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('|') or (table_lines and re.match(r'^[\s]*[\|\-\:]+\s*$', line)):
            table_lines.append(line)
            i += 1
        elif not line.strip() and len(table_lines) > 0:
            # Empty line after table
            break
        elif len(table_lines) > 0:
            # Non-table row
            break
        else:
            break
    return table_lines, i


def _collect_quote(lines: List[str], start: int) -> Tuple[List[str], int]:
    """Collect quote block"""
    quote_lines = []
    i = start
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith('>') or (
                quote_lines and line.strip() and not _is_block_starter(line)):
            quote_lines.append(line)
            i += 1
        elif not line.strip() and quote_lines:
            # Check if next line is still a quote
            if i + 1 < len(lines) and lines[i + 1].strip().startswith('>'):
                quote_lines.append(line)
                i += 1
            else:
                break
        else:
            break
    return quote_lines, i


def _collect_list(lines: List[str], start: int, list_type: str) -> Tuple[List[str], int]:
    """Collect list"""
    list_lines = []
    i = start

    if list_type == 'unordered':
        pattern = r'^[\s]*[-\*\+]\s+'
    else:
        pattern = r'^[\s]*\d+\.\s+'

    while i < len(lines):
        line = lines[i]

        # List item
        if re.match(pattern, line):
            list_lines.append(line)
            i += 1
            continue

        # Continuation line of list item (indented content starting with spaces)
        if line.startswith('  ') or line.startswith('\t'):
            list_lines.append(line)
            i += 1
            continue

        # Nested list
        if re.match(r'^[\s]+[-\*\+]\s+', line) or re.match(r'^[\s]+\d+\.\s+', line):
            list_lines.append(line)
            i += 1
            continue

        # Empty line might be a separator within list
        if not line.strip() and list_lines:
            # Check if next line is still a list
            if i + 1 < len(lines) and (
                    re.match(pattern, lines[i + 1]) or lines[i + 1].startswith('  ')):
                list_lines.append(line)
                i += 1
                continue
            else:
                break

        break

    return list_lines, i


def _collect_paragraph(lines: List[str], start: int) -> Tuple[List[str], int]:
    """Collect regular paragraph"""
    para_lines = []
    i = start
    while i < len(lines):
        line = lines[i]

        # Empty line ends paragraph
        if not line.strip():
            break

        # Encounter other block-level elements
        if _is_block_starter(line):
            if not para_lines:  # First line is a block element
                para_lines.append(line)
                i += 1
            break

        para_lines.append(line)
        i += 1

    return para_lines, i


def _is_block_starter(line: str) -> bool:
    """Determine if this is the start of a block-level element"""
    line_stripped = line.strip()

    # Heading
    if re.match(r'^#{1,6}\s+', line_stripped):
        return True
    # List
    if re.match(r'^[-\*\+]\s+', line_stripped):
        return True
    if re.match(r'^\d+\.\s+', line_stripped):
        return True
    # Quote
    if line_stripped.startswith('>'):
        return True
    # Table
    if line_stripped.startswith('|'):
        return True
    # Horizontal rule
    if re.match(r'^[\-\*_]{3,}\s*$', line_stripped):
        return True

    return False


def _should_translate(text: str) -> bool:
    """Determine if text needs translation"""
    if not text or not text.strip():
        return False

    # Check after removing placeholders
    clean_text = re.sub(r'⟦[A-Z_]+_\d+⟧', '', text)
    clean_text = clean_text.strip()

    if not clean_text:
        return False

    if common.is_all_punc(clean_text):
        return False

    return True


def _split_table(table_lines: List[str]) -> List[str]:
    """Split large table (keep header)"""
    if len(table_lines) <= 2:
        return ['\n'.join(table_lines)]

    header = table_lines[0]
    separator = table_lines[1] if len(table_lines) > 1 and re.match(r'^[\s]*[\|\-\:\s]+$',
                                                                    table_lines[1]) else None

    chunks = []
    current_chunk = [header]
    if separator:
        current_chunk.append(separator)
        data_start = 2
    else:
        data_start = 1

    current_size = len('\n'.join(current_chunk))

    for line in table_lines[data_start:]:
        if current_size + len(line) + 1 > MAX_CHUNK_SIZE:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [header]
            if separator:
                current_chunk.append(separator)
            current_size = len('\n'.join(current_chunk))

        current_chunk.append(line)
        current_size += len(line) + 1

    if current_chunk and len(current_chunk) > (2 if separator else 1):
        chunks.append('\n'.join(current_chunk))

    return chunks if chunks else ['\n'.join(table_lines)]


def _split_quote(quote_lines: List[str]) -> List[str]:
    """Split large quote block"""
    chunks = []
    current_chunk = []
    current_size = 0

    for line in quote_lines:
        if current_size + len(line) + 1 > MAX_CHUNK_SIZE:
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
            current_chunk = [line]
            current_size = len(line)
        else:
            current_chunk.append(line)
            current_size += len(line) + 1

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks if chunks else ['\n'.join(quote_lines)]


def _split_list(list_lines: List[str]) -> List[str]:
    """
    Split large list
    Try to split by complete list items
    """
    # Identify start positions of list items
    item_starts = []
    for i, line in enumerate(list_lines):
        if re.match(r'^[\s]*[-\*\+]\s+', line) or re.match(r'^[\s]*\d+\.\s+', line):
            item_starts.append(i)

    if not item_starts:
        return ['\n'.join(list_lines)]

    # Group by list items
    items = []
    for i, start in enumerate(item_starts):
        end = item_starts[i + 1] if i + 1 < len(item_starts) else len(list_lines)
        items.append(list_lines[start:end])

    # Merge list items until approaching MAX_CHUNK_SIZE
    chunks = []
    current_chunk = []
    current_size = 0

    for item in items:
        item_text = '\n'.join(item)
        item_size = len(item_text)

        if current_size + item_size + 1 > MAX_CHUNK_SIZE:
            if current_chunk:
                chunks.append('\n'.join(['\n'.join(it) for it in current_chunk]))
            current_chunk = [item]
            current_size = item_size
        else:
            current_chunk.append(item)
            current_size += item_size + 1

    if current_chunk:
        chunks.append('\n'.join(['\n'.join(it) for it in current_chunk]))

    return chunks if chunks else ['\n'.join(list_lines)]


def _split_by_sentences_md(text: str) -> List[str]:
    """Split Markdown paragraph at sentence boundaries"""
    # Sentence ending markers
    sentence_endings = r'([.!?。！？][\s]*)'

    parts = re.split(sentence_endings, text)

    # Recombine
    sentences = []
    i = 0
    while i < len(parts):
        sentence = parts[i]
        if i + 1 < len(parts) and re.match(sentence_endings, parts[i + 1]):
            sentence += parts[i + 1]
            i += 2
        else:
            i += 1
        if sentence.strip():
            sentences.append(sentence)

    # Merge sentences
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(sentence) > MAX_CHUNK_SIZE:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            for j in range(0, len(sentence), MAX_CHUNK_SIZE):
                chunk = sentence[j:j + MAX_CHUNK_SIZE]
                if chunk.strip():
                    chunks.append(chunk.strip())
            continue

        if len(current_chunk) + len(sentence) <= MAX_CHUNK_SIZE:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def _make_text_item(text: str, skip: bool = False, block_type: str = 'paragraph',
                    is_sub: bool = False, sub_index: int = 0, sub_total: int = 1,
                    prefix: str = '', content_text: str = '') -> Dict:
    """Create text block object"""
    return {
        'text': text,
        'original': text,
        'complete': skip,
        'skip': skip,
        'count': 0,
        'block_type': block_type,
        'is_sub': is_sub,
        'sub_index': sub_index,
        'sub_total': sub_total,
        'prefix': prefix,  # # prefix for headings
        'content_text': content_text  # Actual content for headings
    }


def _write_result(trans: Dict, texts: List[Dict], protected_blocks: List[ProtectedBlock]) -> int:
    """
    Write translation results
    :return: Translation word count statistics
    """
    trans_type = trans.get('type', '')
    only_translation = 'only' in trans_type
    keep_both = 'both' in trans_type
    text_count = 0

    result_parts = []

    # For merging sub-blocks
    sub_original = ""
    sub_translated = ""
    sub_block_type = ""
    in_sub_sequence = False

    for item in texts:
        text_count += item.get('count', 0)
        block_type = item.get('block_type', 'paragraph')

        # Separator
        if block_type == 'separator':
            if in_sub_sequence:
                _flush_sub_block(result_parts, sub_original, sub_translated,
                                 only_translation, keep_both)
                sub_original = ""
                sub_translated = ""
                in_sub_sequence = False
            result_parts.append("")
            continue

        original = item.get('original', '')
        translated = item.get('text', original)

        if item.get('is_sub', False):
            sub_original += original
            sub_translated += translated
            sub_block_type = block_type
            in_sub_sequence = True

            if item.get('sub_index', 0) == item.get('sub_total', 1) - 1:
                _flush_sub_block(result_parts, sub_original, sub_translated,
                                 only_translation, keep_both)
                sub_original = ""
                sub_translated = ""
                in_sub_sequence = False
        else:
            if item.get('skip', False):
                result_parts.append(original)
            elif keep_both:
                result_parts.append(original)
                result_parts.append(translated)
            elif only_translation:
                result_parts.append(translated)
            else:
                result_parts.append(original)
                result_parts.append(translated)

    # Handle remaining sub-blocks
    if in_sub_sequence:
        _flush_sub_block(result_parts, sub_original, sub_translated,
                         only_translation, keep_both)

    # Merge results
    content = '\n'.join(result_parts)

    # Restore protected blocks
    for block in protected_blocks:
        content = content.replace(block.placeholder, block.content)

    with open(trans['target_file'], 'w', encoding='utf-8') as f:
        f.write(content)

    return text_count


def _flush_sub_block(result_parts: List[str], original: str, translated: str,
                     only_translation: bool, keep_both: bool):
    """Output merged sub-block results"""
    if not original and not translated:
        return

    if keep_both:
        result_parts.append(original)
        result_parts.append(translated)
    elif only_translation:
        result_parts.append(translated)
    else:
        result_parts.append(original)
        result_parts.append(translated)
