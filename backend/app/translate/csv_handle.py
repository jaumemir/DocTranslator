# translate/csv_handle.py
import os
import datetime
import csv
import logging
import re
from typing import List, Dict, Any, Tuple
from threading import Event
from . import to_translate
from . import common

# Chunk configuration
MAX_CHUNK_SIZE = 1500


def start(trans: Dict[str, Any]) -> bool:
    """
    CSV file translation entry point
    :param trans: Translation configuration dictionary
    :return: Whether successful
    """
    translate_id = trans['id']
    start_time = datetime.datetime.now()

    # Read CSV file
    try:
        content, encoding, dialect = _read_csv_file(trans['file_path'])
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to read CSV file: {e}")
        to_translate.error(translate_id, f"Failed to read CSV file: {str(e)}")
        return False

    if not content:
        logging.info(f"[Task {translate_id}] CSV file is empty")
        _write_csv_file(trans['target_file'], content, encoding, dialect)
        to_translate.complete(trans, 0, "0 seconds")
        return True

    # Extract cells that need translation
    texts = []
    cell_map = []  # Record cell positions

    for row_idx, row in enumerate(content):
        for col_idx, cell in enumerate(row):
            if _should_translate(cell):
                # Check if chunking is needed
                if len(cell) > MAX_CHUNK_SIZE:
                    sub_cells = _split_cell(cell, MAX_CHUNK_SIZE)
                    parent_uid = f"cell_{row_idx}_{col_idx}"
                    for i, sub_cell in enumerate(sub_cells):
                        texts.append({
                            'text': sub_cell,
                            'original': sub_cell,
                            'complete': False,
                            'count': 0,
                            '_uid': f"{parent_uid}_{i}",
                            'is_sub': True,
                            'sub_index': i,
                            'sub_total': len(sub_cells)
                        })
                        cell_map.append({
                            'row': row_idx,
                            'col': col_idx,
                            'text_index': len(texts) - 1,
                            'is_sub': True,
                            'parent_uid': parent_uid
                        })
                else:
                    uid = f"cell_{row_idx}_{col_idx}"
                    texts.append({
                        'text': cell,
                        'original': cell,
                        'complete': False,
                        'count': 0,
                        '_uid': uid,
                        'is_sub': False
                    })
                    cell_map.append({
                        'row': row_idx,
                        'col': col_idx,
                        'text_index': len(texts) - 1,
                        'is_sub': False
                    })

    if not texts:
        logging.info(f"[Task {translate_id}] No content to translate in CSV")
        _write_csv_file(trans['target_file'], content, encoding, dialect)
        to_translate.complete(trans, 0, "0 seconds")
        return True

    logging.info(f"[Task {translate_id}] Extracted {len(texts)} text blocks")

    # Batch translation
    event = Event()
    success = to_translate.translate_batch(trans, texts, event)
    if not success:
        return False

    # Rebuild CSV content
    try:
        text_count = _rebuild_csv(content, texts, cell_map, trans.get('type', ''))
        _write_csv_file(trans['target_file'], content, encoding, dialect)
    except Exception as e:
        logging.error(f"[Task {translate_id}] Failed to write CSV file: {e}")
        to_translate.error(translate_id, f"Failed to write CSV file: {str(e)}")
        return False

    end_time = datetime.datetime.now()
    spend_time = common.display_spend(start_time, end_time)
    to_translate.complete(trans, text_count, spend_time)
    return True


def _read_csv_file(file_path: str) -> Tuple[List[List[str]], str, Any]:
    """
    Read CSV file, try multiple encodings and delimiters
    :return: (content list, encoding used, csv dialect)
    """
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'iso-8859-1', 'big5']

    # First try to detect delimiter
    with open(file_path, 'rb') as f:
        sample = f.read(1024).decode('utf-8', errors='ignore')
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
        except:
            dialect = csv.excel  # Default to Excel CSV format

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.reader(f, dialect=dialect)
                content = list(reader)
            return content, encoding, dialect
        except UnicodeDecodeError:
            continue
        except Exception as e:
            raise

    raise ValueError("Unable to recognize CSV file encoding")


def _write_csv_file(file_path: str, content: List[List[str]],
                    encoding: str = 'utf-8', dialect: Any = None):
    """
    Write CSV file, maintain original format
    """
    if dialect is None:
        dialect = csv.excel

    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w', encoding=encoding, newline='') as f:
        writer = csv.writer(f, dialect=dialect)
        writer.writerows(content)


def _should_translate(text) -> bool:
    """
    Check if cell needs translation
    Filter numbers, dates, formulas and other content that doesn't need translation
    """
    if text is None:
        return False

    # Convert to string
    if not isinstance(text, str):
        # Try converting number to string for further checks
        try:
            text = str(text)
        except:
            return False

    text = text.strip()
    if not text:
        return False

    # Skip pure punctuation
    if common.is_all_punc(text):
        return False

    # Skip pure numbers (including scientific notation)
    if re.match(r'^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?%?$', text):
        return False

    # Skip currency format
    if re.match(r'^[$￥€£]\s*[+-]?(\d{1,3}(,\d{3})*(\.\d+)?|\.\d+)$', text):
        return False

    # Skip percentage format
    if re.match(r'^[+-]?(\d{1,3}(,\d{3})*(\.\d+)?|\.\d+)%$', text):
        return False

    # Skip date formats
    date_patterns = [
        r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$',  # 2023-12-31
        r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$',  # 12-31-2023
        r'^\d{1,2}\.\d{1,2}\.\d{4}$',  # 31.12.2023
        r'^[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}$',  # Dec 31, 2023
        r'^\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}$',  # 31 Dec 2023
    ]
    for pattern in date_patterns:
        if re.match(pattern, text):
            return False

    # Skip time formats
    time_patterns = [
        r'^\d{1,2}:\d{2}(:\d{2})?(\s*[AP]M)?$',  # 12:30 PM
        r'^\d{1,2}:\d{2}(:\d{2})?(\s*[ap]m)?$',  # 12:30 pm
    ]
    for pattern in time_patterns:
        if re.match(pattern, text):
            return False

    # Skip boolean values
    if text.lower() in ['true', 'false', 'yes', 'no', 'y', 'n']:
        return False

    # Skip common identifiers
    if re.match(r'^[A-Z]{2,4}\d{1,6}$', text):  # SKU123
        return False

    # Skip emails
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', text):
        return False

    # Skip URLs
    if re.match(r'^https?://', text):
        return False

    # Skip file paths
    if re.match(r'^[A-Za-z]:\\', text) or (text.startswith('/') and '\\' in text):
        return False

    # Skip phone numbers
    if re.match(r'^[\+]?[1-9][\d\-\s\(\)]{7,15}$', text):
        return False

    return True


def _split_cell(cell: str, max_length: int) -> List[str]:
    """
    Split overly long cell content
    Prioritize splitting by sentence boundaries to maintain semantic integrity
    """
    # Split by sentences (supports Chinese and English)
    sentence_pattern = r'(?<=[.!?。！？；;])\s+'
    sentences = re.split(sentence_pattern, cell)

    parts = []
    current_part = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If current part plus new sentence exceeds limit
        if len(current_part) + len(sentence) + 1 > max_length:
            if current_part:
                parts.append(current_part)
                current_part = ""

            # If single sentence exceeds limit, force split by character
            if len(sentence) > max_length:
                for i in range(0, len(sentence), max_length):
                    parts.append(sentence[i:i + max_length])
            else:
                current_part = sentence
        else:
            if current_part:
                current_part += " " + sentence
            else:
                current_part = sentence

    if current_part:
        parts.append(current_part)

    return parts if parts else [cell]


def _rebuild_csv(content: List[List[str]], texts: List[Dict],
                 cell_map: List[Dict], trans_type: str) -> int:
    """
    Rebuild CSV content, handle chunk merging
    """
    text_count = 0
    keep_both = 'both' in trans_type

    # Process by cell grouping
    cell_translations = {}  # (row, col) -> {'original': str, 'translated': str}

    for mapping in cell_map:
        row = mapping['row']
        col = mapping['col']
        text_index = mapping['text_index']
        is_sub = mapping.get('is_sub', False)

        if text_index >= len(texts):
            continue

        text_item = texts[text_index]
        text_count += text_item.get('count', 0)

        key = (row, col)
        if key not in cell_translations:
            cell_translations[key] = {
                'original': '',
                'translated': ''
            }

        if is_sub:
            # Chunked content needs to be merged
            cell_translations[key]['original'] += text_item.get('original', '')
            cell_translations[key]['translated'] += text_item.get('text', '')
        else:
            cell_translations[key]['original'] = text_item.get('original', '')
            cell_translations[key]['translated'] = text_item.get('text', '')

    # Apply translation results
    for (row, col), trans_data in cell_translations.items():
        if row < len(content) and col < len(content[row]):
            original = trans_data['original'].strip()
            translated = trans_data['translated'].strip()

            if keep_both:
                # Bilingual mode: keep both original and translated
                if original and translated:
                    content[row][col] = f"{original}\n{translated}"
                else:
                    content[row][col] = translated or original
            else:
                # Translation-only mode
                content[row][col] = translated or original

    return text_count
