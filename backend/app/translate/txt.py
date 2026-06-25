# translate/txt.py
"""
TXT file translation processor
Chunking strategy:
1. Split paragraphs by empty lines
2. Maintain paragraph integrity
3. Split oversized paragraphs at sentence boundaries
4. Skip pure punctuation/number lines
"""

import re
import datetime
import logging
from threading import Event
from typing import List, Dict, Tuple
from . import to_translate
from . import common

# Chunking configuration
MAX_CHUNK_SIZE = 2000


def start(trans: Dict) -> bool:
    """
    TXT file translation entry point
    :param trans: Translation configuration dictionary
    :return: Whether successful
    """
    translate_id = trans['id']
    start_time = datetime.datetime.now()

    # Read file
    try:
        content, encoding = _read_file(trans['file_path'])
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to read file: {e}")
        to_translate.error(translate_id, f"Failed to read file: {str(e)}")
        return False

    if not content or not content.strip():
        logging.info(f"[Task {translate_id}] File content is empty")
        _write_file(trans['target_file'], "")
        to_translate.complete(trans, 0, "0s")
        return True

    # Smart chunking
    texts = _smart_chunk(content)

    # Count blocks that need translation
    to_translate_count = sum(1 for t in texts if not t.get('skip', False))

    if to_translate_count == 0:
        logging.info(f"[Task {translate_id}] No content to translate")
        _write_file(trans['target_file'], content)
        to_translate.complete(trans, 0, "0s")
        return True

    logging.info(
        f"[Task {translate_id}] Split into {len(texts)} blocks, {to_translate_count} need translation")

    # Execute translation
    event = Event()
    success = to_translate.translate_batch(trans, texts, event)
    if not success:
        return False

    # Write results
    try:
        text_count = _write_result(trans, texts)
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to write file: {e}")
        to_translate.error(translate_id, f"Failed to write file: {str(e)}")
        return False

    end_time = datetime.datetime.now()
    spend_time = common.display_spend(start_time, end_time)
    to_translate.complete(trans, text_count, spend_time)
    return True


def _read_file(file_path: str) -> Tuple[str, str]:
    """
    Read file content, try multiple encodings
    :return: (content, encoding used)
    """
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5', 'iso-8859-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise

    raise ValueError("Unable to recognize file encoding")


def _write_file(file_path: str, content: str):
    """Write file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _smart_chunk(content: str) -> List[Dict]:
    """
    Smart chunking strategy:
    1. Split into paragraphs by empty lines
    2. Maintain paragraph integrity
    3. Split oversized paragraphs at sentence boundaries
    """
    texts = []

    # Normalize line breaks
    content = content.replace('\r\n', '\n').replace('\r', '\n')

    # Split by empty lines (one or more empty lines)
    paragraphs = re.split(r'\n\s*\n', content)

    for para in paragraphs:
        para = para.strip()

        # Empty paragraph, keep as separator
        if not para:
            texts.append(_make_text_item('', skip=True, is_separator=True))
            continue

        # Check if translation is needed
        if not _should_translate(para):
            texts.append(_make_text_item(para, skip=True))
            continue

        # Check length
        if len(para) <= MAX_CHUNK_SIZE:
            # Paragraph doesn't exceed limit, use whole paragraph as one block
            texts.append(_make_text_item(para))
        else:
            # Oversized paragraph, split at sentence boundaries
            sub_chunks = _split_by_sentences(para, MAX_CHUNK_SIZE)
            for i, chunk in enumerate(sub_chunks):
                texts.append(_make_text_item(
                    chunk,
                    is_sub=True,
                    sub_index=i,
                    sub_total=len(sub_chunks)
                ))

    return texts


def _should_translate(text: str) -> bool:
    """Determine if text needs translation"""
    if not text or not text.strip():
        return False

    text = text.strip()

    # Pure punctuation/numbers/whitespace
    if common.is_all_punc(text):
        return False

    # Pure numbers (possibly page numbers, sequence numbers, etc.)
    if re.match(r'^[\d\s\.\-\+\*\/\=\%\(\)]+$', text):
        return False

    return True


def _split_by_sentences(text: str, max_size: int) -> List[str]:
    """
    Split long text at sentence boundaries
    Prioritize maintaining sentence integrity
    """
    # Sentence ending markers (Chinese and English)
    sentence_endings = r'([.!?。！？；;][\s]*)'

    # Split by sentences, keep delimiters
    parts = re.split(sentence_endings, text)

    # Recombine (sentence + punctuation)
    sentences = []
    i = 0
    while i < len(parts):
        sentence = parts[i]
        # If next is punctuation, merge
        if i + 1 < len(parts) and re.match(sentence_endings, parts[i + 1]):
            sentence += parts[i + 1]
            i += 2
        else:
            i += 1
        if sentence.strip():
            sentences.append(sentence)

    # Merge sentences until approaching max_size
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        # Single sentence exceeds limit, needs forced splitting
        if len(sentence) > max_size:
            # Save current block first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            # Force split oversized sentence by characters
            for j in range(0, len(sentence), max_size):
                chunk = sentence[j:j + max_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
            continue

        # Check if can merge
        if len(current_chunk) + len(sentence) <= max_size:
            current_chunk += sentence
        else:
            # Current block is full, save and start new block
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence

    # Save last block
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def _make_text_item(text: str, skip: bool = False, is_sub: bool = False,
                    sub_index: int = 0, sub_total: int = 1,
                    is_separator: bool = False) -> Dict:
    """Create text block object"""
    return {
        'text': text,
        'original': text,
        'complete': skip,  # Skipped blocks marked as complete
        'skip': skip,
        'count': 0,
        'is_sub': is_sub,  # Whether it's a split sub-block
        'sub_index': sub_index,
        'sub_total': sub_total,
        'is_separator': is_separator  # Whether it's a paragraph separator
    }


def _write_result(trans: Dict, texts: List[Dict]) -> int:
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
    in_sub_sequence = False

    for item in texts:
        text_count += item.get('count', 0)

        # Paragraph separator
        if item.get('is_separator', False):
            # Process previous sub-block sequence first
            if in_sub_sequence:
                if keep_both:
                    result_parts.append(sub_original)
                    result_parts.append(sub_translated)
                elif only_translation:
                    result_parts.append(sub_translated)
                else:
                    result_parts.append(sub_original)
                    result_parts.append(sub_translated)
                sub_original = ""
                sub_translated = ""
                in_sub_sequence = False
            result_parts.append("")  # Empty line separator
            continue

        original = item.get('original', '')
        translated = item.get('text', original)

        if item.get('is_sub', False):
            # Sub-block, accumulate
            sub_original += original
            sub_translated += translated
            in_sub_sequence = True

            # If it's the last sub-block, output
            if item.get('sub_index', 0) == item.get('sub_total', 1) - 1:
                if keep_both:
                    result_parts.append(sub_original)
                    result_parts.append(sub_translated)
                elif only_translation:
                    result_parts.append(sub_translated)
                else:
                    result_parts.append(sub_original)
                    result_parts.append(sub_translated)
                sub_original = ""
                sub_translated = ""
                in_sub_sequence = False
        else:
            # Regular block
            if item.get('skip', False):
                # Keep original for skipped blocks
                result_parts.append(original)
            elif keep_both:
                result_parts.append(original)
                result_parts.append(translated)
            elif only_translation:
                result_parts.append(translated)
            else:
                result_parts.append(original)
                result_parts.append(translated)

    # Handle potentially remaining sub-blocks
    if in_sub_sequence:
        if keep_both:
            result_parts.append(sub_original)
            result_parts.append(sub_translated)
        elif only_translation:
            result_parts.append(sub_translated)
        else:
            result_parts.append(sub_original)
            result_parts.append(sub_translated)

    # Merge output, separate paragraphs with double newlines
    content = '\n\n'.join(result_parts)

    _write_file(trans['target_file'], content)

    return text_count
