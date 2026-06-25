# translate/to_translate.py
import logging
import re
import time
import openai
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import  Lock
from . import common
from . import db

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Progress update lock
_progress_lock = Lock()

_last_reported_progress = {}  # Store last reported progress for each task {task_id: progress}


def update_progress(texts, translate_id, force_update=False):
    """
    Smart update of translation progress
    :param texts: List of text blocks
    :param translate_id: Task ID
    :param force_update: Whether to force update (used when task completes)
    """
    total = len(texts)
    completed = sum(1 for t in texts if t.get('complete', False))

    if total <= 0:
        return

    current_progress = round((completed / total) * 100, 1)

    with _progress_lock:
        last_progress = _last_reported_progress.get(translate_id, 0)

        # Progress update conditions:
        # 1. Force update (task complete/failed)
        # 2. Progress increased by more than 15%
        # 3. First update (from 0)
        # 4. Special handling near completion (every 10% above 90%)
        progress_delta = current_progress - last_progress

        should_update = (
                force_update or
                progress_delta >= 15.0 or  # Update every 15%
                (last_progress == 0 and current_progress > 0) or  # First progress
                (current_progress >= 90 and progress_delta >= 10.0)  # Every 10% after 90%
        )

        if should_update:
            try:
                db.execute("UPDATE translate SET process=%s WHERE id=%s",
                           current_progress, translate_id)
                _last_reported_progress[translate_id] = current_progress
                logging.info(f"[Task{translate_id}] Progress update: {current_progress}%")
            except Exception as e:
                logging.error(f"Failed to update progress: {e}")


def complete(trans, text_count, spend_time):
    """Mark task as completed"""
    try:
        translate_id = trans['id']
        target_filesize = 1

        db.execute(
            "UPDATE translate SET status='done', end_at=NOW(), process=100, "
            "target_filesize=%s, word_count=%s WHERE id=%s",
            target_filesize, text_count, translate_id
        )

        # Clean up progress cache
        _last_reported_progress.pop(translate_id, None)

        logging.info(f"[Task{translate_id}] Translation completed")

    except Exception as e:
        logging.error(f"Failed to update completion status: {e}")


def error(translate_id, message):
    """Mark task as failed"""
    try:
        message = str(message)[:500] if message else "Unknown error"

        # Clean up progress cache
        _last_reported_progress.pop(translate_id, None)

        db.execute(
            "UPDATE translate SET failed_count=failed_count+1, status='failed', "
            "end_at=NOW(), failed_reason=%s WHERE id=%s",
            message, translate_id
        )
    except Exception as e:
        logging.error(f"Failed to update failure status: {e}")


class TranslationError(Exception):
    """Base class for translation exceptions"""
    pass


class FatalError(TranslationError):
    """Fatal error, not retryable"""
    pass


def translate_batch(trans, texts, event):
    """
    Batch translate text blocks (thread pool mode)
    :param trans: Translation configuration
    :param texts: List of text blocks
    :param event: Interruption event
    :return: Whether all succeeded
    """
    translate_id = trans['id']
    max_threads = common.parse_threads(trans.get('threads'))

    # Filter indices of text blocks that need translation
    to_translate_indices = [
        i for i, t in enumerate(texts)
        if not t.get('complete', False) and not t.get('skip', False)
    ]

    if not to_translate_indices:
        return True

    logging.info(
        f"[Task{translate_id}] Starting translation of {len(to_translate_indices)} text blocks, threads: {max_threads}")

    has_fatal_error = False
    completed_count = 0
    total_count = len(to_translate_indices)

    def translate_single(index):
        """Translate a single text block"""
        nonlocal has_fatal_error, completed_count

        if event.is_set() or has_fatal_error:
            return False

        text_item = texts[index]

        try:
            result = _translate_text_block(trans, text_item)
            text_item['text'] = result['translated_text']
            text_item['count'] = result['count']
            text_item['complete'] = True

            # Update progress
            with _progress_lock:
                completed_count += 1
                progress = round((completed_count / total_count) * 100, 1)
                db.execute("UPDATE translate SET process=%s WHERE id=%s", progress, translate_id)

            return True

        except FatalError as e:
            logging.error(f"[Task{translate_id}] Fatal error: {str(e)}")
            has_fatal_error = True
            error(translate_id, str(e))
            event.set()
            return False

        except Exception as e:
            logging.error(f"[Task{translate_id}] Text block {index} translation failed, keeping original: {str(e)}")
            text_item['complete'] = True
            text_item['count'] = count_text(text_item.get('text', ''))

            with _progress_lock:
                completed_count += 1

            return True  # Keep original text, continue processing other blocks

    # Execute with thread pool
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Submit all tasks
        future_to_index = {
            executor.submit(translate_single, idx): idx
            for idx in to_translate_indices
        }

        # Wait for completion
        for future in as_completed(future_to_index):
            if event.is_set() or has_fatal_error:
                # Cancel remaining tasks
                executor.shutdown(wait=False, cancel_futures=True)
                return False

            try:
                future.result()
            except Exception as e:
                logging.error(f"[Task{translate_id}] Thread execution exception: {e}")

    return not has_fatal_error


def get(trans, event, texts, index):
    """
    Entry function for translating a single text block (legacy interface compatibility)
    :param trans: Translation task configuration
    :param event: Thread event for interruption
    :param texts: List of text blocks
    :param index: Current processing index
    """
    if event.is_set():
        return

    text_item = texts[index]
    translate_id = trans['id']

    try:
        # Execute translation
        result = _translate_text_block(trans, text_item)

        # Update results
        text_item['text'] = result['translated_text']
        text_item['count'] = result['count']
        text_item['complete'] = True

    except FatalError as e:
        # Fatal error, mark task as failed
        logging.error(f"[Task{translate_id}] Fatal error: {str(e)}")
        if not event.is_set():
            error(translate_id, str(e))
        event.set()
        return

    except Exception as e:
        # Other errors, keep original text, mark as complete
        logging.error(f"[Task{translate_id}] Text block {index} translation failed, keeping original: {str(e)}")
        text_item['complete'] = True
        text_item['count'] = count_text(text_item.get('text', ''))

    finally:
        texts[index] = text_item
        if not event.is_set():
            update_progress(texts, translate_id)


def _translate_text_block(trans, text_item):
    """
    Translate a single text block, including retry and backup model logic
    :return: {'translated_text': str, 'count': int}
    """
    original_text = text_item.get('text', '')
    if not original_text or not original_text.strip():
        return {'translated_text': original_text, 'count': 0}

    server = trans.get('server', 'openai')

    # Baidu Translate doesn't have backup model concept
    if server == 'baidu':
        result = _try_translate_with_retries(trans, text_item, 'baidu')
        if result:
            return result
        raise FatalError("Baidu translation failed")
    else:
        # OpenAI and similar APIs have backup models
        model = trans.get('model')
        backup_model = trans.get('backup_model')

        # Try primary model
        result = _try_translate_with_retries(trans, text_item, model)
        if result:
            return result

        # Primary model failed, try backup model
        if backup_model and backup_model.strip():
            logging.info(f"[Task{trans['id']}] Primary model {model} failed, switching to backup model {backup_model}")
            time.sleep(RETRY_DELAY)
            result = _try_translate_with_retries(trans, text_item, backup_model)
            if result:
                return result

        # All failed
        raise FatalError(f"Both primary and backup models failed, last model used: {backup_model or model}")


def _try_translate_with_retries(trans, text_item, model):
    """
    Retry translation with specified model
    :return: Returns result dict on success, None on failure
    """
    translate_id = trans['id']
    original_text = text_item.get('text', '')

    for attempt in range(1, MAX_RETRIES + 1):
        try:

            # Execute translation
            server = trans.get('server', 'openai')
            if server == 'baidu':
                logging.info(f"[Task{translate_id}] Baidu translation attempt {attempt}")
                translated = _translate_baidu(trans, original_text)
            else:
                logging.info(f"[Task{translate_id}] Translation model {model}, attempt {attempt}")
                translated = _translate_openai(trans, original_text, model)

            # Validate translation result
            if not _is_valid_translation(translated):
                logging.warning(
                    f"Type: {trans.get('server', '')}——[Task{translate_id}] Invalid translation result: {translated[:50] if translated else 'None'}...")
                time.sleep(RETRY_DELAY)
                continue

            # Filter deepseek thinking tags
            translated = re.sub(r'', '', translated, flags=re.DOTALL).strip()

            return {'translated_text': translated, 'count': count_text(original_text)}

        except openai.RateLimitError as e:
            logging.warning(f"[Task{translate_id}] Rate limit, retrying after wait: {e}")
            time.sleep(RETRY_DELAY * attempt * 2)  # Incremental wait, longer for rate limits
            continue

        except openai.AuthenticationError as e:
            raise FatalError(f"Invalid API key: {e}")

        except openai.APIConnectionError as e:
            logging.warning(f"[Task{translate_id}] Connection error: {e}")
            time.sleep(RETRY_DELAY)
            continue

        except Exception as e:
            logging.warning(f"[Task{translate_id}] Translation exception: {e}")
            time.sleep(RETRY_DELAY)
            continue

    return None  # All retries failed


def _translate_openai(trans, text, model):
    """Call OpenAI-compatible API for translation"""
    target_lang = trans.get('lang', 'English')
    base_prompt = trans.get('prompt', '')
    extension = trans.get('extension', '').lower()

    # Dynamically match terms and inject into prompt
    final_prompt = _inject_matched_terms(trans, text, base_prompt, target_lang)

    # Special handling for Markdown
    if extension == '.md':
        final_prompt += "\nPlease keep Markdown format unchanged, only translate text content."

    # Special handling for HTML
    if extension in ('.html', '.htm'):
        final_prompt += "\nPlease keep HTML tags and attributes unchanged, only translate text content between tags. Do not add or remove any HTML tags."

    messages = [
        {"role": "system", "content": final_prompt},
        {"role": "user", "content": text}
    ]
    print(f"[Task{trans['id']}] Model {model}, Prompt: {final_prompt}")
    # Disable logging
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    response = openai.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content


def _translate_baidu(trans, text):
    """Call Baidu Translation API"""
    from .baidu.main import baidu_translate

    use_term_base = trans.get('use_baidu_terms', False)

    return baidu_translate(
        text=text,
        appid=trans.get('app_id'),
        app_key=trans.get('app_key'),
        from_lang='auto',
        to_lang=trans.get('lang', 'en'),
        use_term_base=use_term_base
    )


def _inject_matched_terms(trans, text, base_prompt, target_lang):
    """
    Dynamically match terms and inject into prompt
    Uses regular expressions for precise term matching (word boundaries)
    """
    terms_dict = trans.get('terms_dict')
    if not terms_dict:
        logging.debug("No terminology data, skipping term matching")
        return base_prompt.replace("{target_lang}", target_lang)

    matched_terms = []


    for term_pair in terms_dict:
        source_term = term_pair['source']
        target_term = term_pair['target']

        if _is_term_matched_in_text(source_term, text):
            matched_terms.append(f"{source_term} → {target_term}")
            logging.debug(f"Matched term: {source_term} → {target_term}")

    # Build final prompt
    if matched_terms:
        # Deduplicate (prevent duplicate terms)
        unique_terms = list(dict.fromkeys(matched_terms))
        terms_section = "【Terminology Translation Table】\n" + "\n".join(unique_terms)
        full_prompt = f"{terms_section}\n\n{base_prompt}"
    else:
        full_prompt = base_prompt
        logging.debug("No matching terms in current text")

    return full_prompt.replace("{target_lang}", target_lang)


def _is_term_matched_in_text(source_term, text):
    """
    Check if a term is precisely matched in text
    Uses multiple matching strategies to improve accuracy
    """
    if not source_term or not text:
        return False

    source_term = source_term.strip()
    if not source_term:
        return False

    # Strategy 1: Word boundary matching (for English words)
    if _is_word_boundary_match(source_term, text):
        return True

    # Strategy 2: Complete phrase matching (for Chinese phrases, technical terms)
    if _is_phrase_match(source_term, text):
        return True

    # Strategy 3: Mixed language matching (for mixed Chinese-English terms)
    if _is_mixed_language_match(source_term, text):
        return True

    return False


def _is_word_boundary_match(source_term, text):
    """
    Word boundary matching: Use \b for precise word matching
    Suitable for: API, JSON, HTTP, database and other English terms
    """
    try:
        # Escape special characters
        escaped_term = re.escape(source_term)

        # Build word boundary pattern
        pattern = r'\b' + escaped_term + r'\b'

        # Case-insensitive matching
        return bool(re.search(pattern, text, re.IGNORECASE))

    except Exception as e:
        logging.warning(f"Word boundary matching failed: {e}")
        return False


def _is_phrase_match(source_term, text):
    """
    Phrase matching: Suitable for Chinese phrases or multi-word terms
    Uses punctuation and whitespace as boundaries
    Suitable for: artificial intelligence, machine learning, REST API, etc.
    """
    try:
        # Escape special characters
        escaped_term = re.escape(source_term)

        # Define phrase boundaries: whitespace, punctuation, line start/end
        boundary = r'(?:^|[\s\p{P}])'  # Start boundary
        end_boundary = r'(?=[\s\p{P}]|$)'  # End boundary

        # Build phrase pattern
        pattern = boundary + escaped_term + end_boundary

        # Case-insensitive matching
        return bool(re.search(pattern, text, re.IGNORECASE))

    except Exception:
        # If regex doesn't support \p{P}, use common punctuation marks
        try:
            escaped_term = re.escape(source_term)
            punctuation = r'[\s.,!?;:()\[\]{}"\'`~@#$%^&*+=|\\/<>，。！？；：（）【】{}""''`～@#￥%…&*+=|\\/<>]'
            boundary = r'(?:^|' + punctuation + r')'
            end_boundary = r'(?=' + punctuation + r'|$)'
            pattern = boundary + escaped_term + end_boundary

            return bool(re.search(pattern, text, re.IGNORECASE))
        except Exception as e:
            logging.warning(f"Phrase matching failed: {e}")
            return False


def _is_mixed_language_match(source_term, text):
    """
    Mixed language matching: Suitable for mixed Chinese-English terms
    Examples: API interface, JSON data, HTTP request, etc.
    """
    try:
        # Split term by Chinese and English characters
        parts = _split_mixed_term(source_term)
        if len(parts) <= 1:
            return False

        # Check if all parts exist in correct order
        current_pos = 0
        text_lower = text.lower()

        for part in parts:
            part_lower = part.lower()
            pos = text_lower.find(part_lower, current_pos)
            if pos == -1:
                return False
            current_pos = pos + len(part)

        return True

    except Exception as e:
        logging.warning(f"Mixed language matching failed: {e}")
        return False


def _split_mixed_term(term):
    """
    Split mixed Chinese-English term
    Example: API接口 -> ["API", "接口"]
    """
    import re

    # Split by Chinese-English character boundaries
    pattern = r'([a-zA-Z]+|[\u4e00-\u9fff]+|[0-9]+)'
    parts = re.findall(pattern, term)

    # Filter empty strings and single characters
    return [p for p in parts if len(p.strip()) > 0]

def _is_valid_translation(content):
    """Validate if translation result is valid"""
    if not content:
        return False
    invalid_prefixes = [
        "Sorry, I cannot", "I am sorry,", "I'm sorry,",
        "Sorry, I can't", "Sorry, I need more", "抱歉，无法",
        "错误：提供的文本", "无法翻译", "抱歉，我无法",
        "对不起，我无法", "ご指示の内容は", "申し訳ございません",
        "Простите，", "Извините,", "Lo siento,"
    ]
    for prefix in invalid_prefixes:
        if content.startswith(prefix):
            return False
    return True


def count_text(text):
    """Count text characters"""
    if not text:
        return 0
    count = 0
    for char in text:
        if common.is_chinese(char):
            count += 1
        elif char and char != " ":
            count += 0.5
    return int(count)


def init_openai(url, key):
    """Initialize OpenAI configuration"""
    openai.api_key = key
    if not url.endswith("/v1/"):
        if url.endswith("/v1"):
            url = url + "/"
        elif url.endswith("/"):
            url = url + "v1/"
        else:
            url = url + "/v1/"
    openai.base_url = url


def check(model):
    """Check model availability"""
    try:
        message = [
            {"role": "system", "content": "Test"},
            {"role": "user", "content": "Hello"}
        ]
        openai.chat.completions.create(model=model, messages=message, max_tokens=10)
        return "OK"
    except openai.AuthenticationError:
        return "Invalid API key"
    except openai.APIConnectionError:
        return "Cannot connect to API server"
    except openai.RateLimitError:
        return "Rate limit exceeded"
    except Exception as e:
        return f"Check failed: {str(e)}"
