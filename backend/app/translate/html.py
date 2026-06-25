# translate/html.py
"""
HTML/HTM file translation handler
Core strategy: Placeholder replacement method
1. Parse HTML with BeautifulSoup
2. Traverse DOM tree, extract all text nodes and attribute values that need translation
3. Replace original text with placeholders, record mapping relationships
4. Chunk and translate extracted text
5. Replace placeholders with translation results according to mapping relationships
6. Restore complete HTML, ensure structure remains completely unchanged
"""

import re
import datetime
import logging
import threading
from typing import List, Dict, Tuple
from . import to_translate
from . import common

MAX_CHUNK_SIZE = 2000

SKIP_TAGS = frozenset({
    'script', 'style', 'noscript'
})

PRESERVE_TAGS = frozenset({
    'code', 'kbd', 'samp', 'var'
})

VOID_TAGS = frozenset({
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr'
})

TRANSLATABLE_ATTRS = frozenset({
    'alt', 'title', 'placeholder', 'aria-label', 'aria-description'
})

_counter_lock = threading.Lock()
_counter = 0

PLACEHOLDER_PREFIX = '[[HTMLTRANS_'
PLACEHOLDER_SUFFIX = ']]'


def _next_placeholder(tag: str) -> str:
    global _counter
    with _counter_lock:
        _counter += 1
        return f'{PLACEHOLDER_PREFIX}{tag}_{_counter}{PLACEHOLDER_SUFFIX}'


def start(trans: Dict) -> bool:
    translate_id = trans['id']
    start_time = datetime.datetime.now()

    try:
        content, encoding = _read_file(trans['file_path'])
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to read file: {e}")
        to_translate.error(translate_id, f"Failed to read file: {str(e)}")
        return False

    if not content or not content.strip():
        logging.info(f"[Task {translate_id}] File content is empty")
        _write_file(trans['target_file'], "")
        to_translate.complete(trans, 0, "0 seconds")
        return True

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        logging.error(f"[Task {translate_id}] Need to install beautifulsoup4")
        to_translate.error(translate_id, "Need to install beautifulsoup4: pip install beautifulsoup4")
        return False

    try:
        soup = BeautifulSoup(content, 'html.parser')
    except Exception as e:
        logging.error(f"[Task {translate_id}] HTML parsing failed: {e}")
        to_translate.error(translate_id, f"HTML parsing failed: {str(e)}")
        return False

    placeholder_map = {}
    extracted_texts = []

    try:
        _extract_and_placeholder(soup, placeholder_map, extracted_texts)
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to extract text nodes: {e}")
        to_translate.error(translate_id, f"Failed to extract text nodes: {str(e)}")
        return False

    if not extracted_texts:
        logging.info(f"[Task {translate_id}] No text content to translate")
        _write_file(trans['target_file'], content)
        to_translate.complete(trans, 0, "0 seconds")
        return True

    texts = _build_text_items(extracted_texts)

    to_translate_count = sum(1 for t in texts if not t.get('skip', False))
    if to_translate_count == 0:
        logging.info(f"[Task {translate_id}] No content to translate")
        _write_file(trans['target_file'], content)
        to_translate.complete(trans, 0, "0 seconds")
        return True

    logging.info(
        f"[Task {translate_id}] Extracted {len(extracted_texts)} text segments, "
        f"{to_translate_count} need translation")

    event = threading.Event()
    success = to_translate.translate_batch(trans, texts, event)
    if not success:
        return False

    try:
        text_count = _write_result(trans, texts, extracted_texts, placeholder_map, soup)
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to write file: {e}")
        to_translate.error(translate_id, f"Failed to write file: {str(e)}")
        return False

    end_time = datetime.datetime.now()
    spend_time = common.display_spend(start_time, end_time)
    to_translate.complete(trans, text_count, spend_time)
    return True


def _read_file(file_path: str) -> Tuple[str, str]:
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030', 'big5', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return content, encoding
        except UnicodeDecodeError:
            continue
        except Exception:
            raise
    raise ValueError("Unable to recognize file encoding")


def _write_file(file_path: str, content: str):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def _extract_and_placeholder(soup, placeholder_map: Dict, extracted_texts: List[Dict]):
    """
    Traverse DOM tree, extract text and replace with placeholders
    All operations completed on the same soup object to ensure valid references
    """
    try:
        from bs4 import NavigableString, Comment, Tag, ProcessingInstruction, Doctype
    except ImportError:
        raise ImportError("需要安装 beautifulsoup4")

    def walk(element, in_preserve: bool = False):
        try:
            if isinstance(element, (Comment, ProcessingInstruction, Doctype)):
                return

            if isinstance(element, NavigableString):
                text = str(element)
                if not text.strip():
                    return

                if in_preserve:
                    ph = _next_placeholder('p')
                    placeholder_map[ph] = text
                    extracted_texts.append({
                        'placeholder': ph,
                        'original': text,
                        'skip': True,
                        'type': 'text'
                    })
                    element.replace_with(NavigableString(ph))
                    return

                if _should_translate(text):
                    ph = _next_placeholder('t')
                    placeholder_map[ph] = text
                    extracted_texts.append({
                        'placeholder': ph,
                        'original': text,
                        'skip': False,
                        'type': 'text'
                    })
                    element.replace_with(NavigableString(ph))
                else:
                    ph = _next_placeholder('s')
                    placeholder_map[ph] = text
                    extracted_texts.append({
                        'placeholder': ph,
                        'original': text,
                        'skip': True,
                        'type': 'text'
                    })
                    element.replace_with(NavigableString(ph))
                return

            if isinstance(element, Tag):
                tag_name = (element.name or '').lower()

                if tag_name in SKIP_TAGS:
                    return

                is_preserve = in_preserve or tag_name in PRESERVE_TAGS

                if tag_name in VOID_TAGS:
                    for attr_name in TRANSLATABLE_ATTRS:
                        attr_val = element.get(attr_name, '')
                        if attr_val and isinstance(attr_val, str) and _should_translate(attr_val):
                            ph = _next_placeholder('a')
                            placeholder_map[ph] = attr_val
                            extracted_texts.append({
                                'placeholder': ph,
                                'original': attr_val,
                                'skip': False,
                                'type': 'attr',
                                'element': element,
                                'attr_name': attr_name
                            })
                            element[attr_name] = ph
                    return

                for child in list(element.children):
                    walk(child, is_preserve)

        except Exception as e:
            logging.warning(f"Exception while traversing DOM node (skipped): {e}")

    for child in list(soup.children):
        walk(child, False)


def _should_translate(text: str) -> bool:
    if not text or not text.strip():
        return False
    text = text.strip()
    if common.is_all_punc(text):
        return False
    if re.match(r'^[\d\s\.\-\+\*\/\=\%\(\)\,]+$', text):
        return False
    if len(text) <= 1:
        return False
    return True


def _build_text_items(extracted_texts: List[Dict]) -> List[Dict]:
    """
    Build extracted text segments into texts list needed by translation engine
    Split overly long text, all sub-blocks after splitting share the same placeholder
    """
    texts = []
    for item in extracted_texts:
        if item['skip']:
            texts.append({
                'text': item['original'],
                'original': item['original'],
                'complete': True,
                'skip': True,
                'count': 0,
                'placeholder': item['placeholder'],
                'is_sub': False
            })
        elif len(item['original']) <= MAX_CHUNK_SIZE:
            texts.append({
                'text': item['original'],
                'original': item['original'],
                'complete': False,
                'skip': False,
                'count': 0,
                'placeholder': item['placeholder'],
                'is_sub': False
            })
        else:
            sub_chunks = _split_by_sentences(item['original'], MAX_CHUNK_SIZE)
            for i, chunk in enumerate(sub_chunks):
                texts.append({
                    'text': chunk,
                    'original': chunk,
                    'complete': False,
                    'skip': False,
                    'count': 0,
                    'placeholder': item['placeholder'],
                    'is_sub': True,
                    'sub_index': i,
                    'sub_total': len(sub_chunks)
                })
    return texts


def _split_by_sentences(text: str, max_size: int) -> List[str]:
    sentence_endings = r'([.!?。！？；;][\s]*)'
    parts = re.split(sentence_endings, text)
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

    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(sentence) > max_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            for j in range(0, len(sentence), max_size):
                chunk = sentence[j:j + max_size]
                if chunk.strip():
                    chunks.append(chunk.strip())
            continue
        if len(current_chunk) + len(sentence) <= max_size:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks if chunks else [text]


def _write_result(trans: Dict, texts: List[Dict], extracted_texts: List[Dict],
                  placeholder_map: Dict, soup) -> int:
    """
    Write translation results
    Steps:
    1. Collect translation results for each placeholder from texts
    2. Directly set attr type translation results to DOM elements
    3. Serialize soup to HTML string
    4. Use string replacement to replace text placeholders with translation results
    HTML files always maintain complete HTML structure output, no only_translation processing
    """
    text_count = 0

    placeholder_translations = {}

    for item in texts:
        if item.get('skip', False):
            placeholder_translations[item['placeholder']] = item['original']
            continue

        translated = item.get('text', item.get('original', ''))
        text_count += item.get('count', 0)
        ph = item['placeholder']

        if item.get('is_sub', False):
            if ph not in placeholder_translations:
                placeholder_translations[ph] = ''
            placeholder_translations[ph] += translated
        else:
            placeholder_translations[ph] = translated

    for item in extracted_texts:
        if item['type'] == 'attr':
            element = item.get('element')
            attr_name = item.get('attr_name')
            if element is not None and attr_name:
                translated_val = placeholder_translations.get(item['placeholder'], item['original'])
                try:
                    element[attr_name] = translated_val
                except Exception as e:
                    logging.warning(f"Failed to replace attribute value: {e}")

    html_str = str(soup)

    for ph, original_text in placeholder_map.items():
        translated_text = placeholder_translations.get(ph, original_text)
        html_str = html_str.replace(ph, translated_text)

    _write_file(trans['target_file'], html_str)

    return text_count
