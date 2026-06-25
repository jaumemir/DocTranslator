import json

import requests
import random
import hashlib



def baidu_translate(
        text: str,
        appid: str,
        app_key: str,
        from_lang: str = 'auto',
        to_lang: str = 'en',
        use_term_base: bool = False,
) -> str:
    """
    Parameters:
        text: Text to translate (multiline text separated by newlines)
        appid: Baidu API APP ID
        key: Baidu API key
        from_lang: Source language code (default auto for auto-detection)
        to_lang: Target language code (default en for English)
        use_term_base: Whether to enable term base (controlled by needIntervene=1)

    """
    # 1. Generate signature parameters
    salt = str(random.randint(32768, 65536))
    sign_str = appid + text + salt + app_key
    sign = hashlib.md5(sign_str.encode()).hexdigest()

    # 2. Construct request parameters
    params = {
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'appid': appid,
        'salt': salt,
        'sign': sign,
    }
    if use_term_base:
        params['needIntervene'] = 1  # Enable term base

    # 3. Send request
    try:
        response = requests.get(
            "https://fanyi-api.baidu.com/api/trans/vip/translate",
            params=params,
            timeout=60
        )
        result = response.json()

        if 'error_code' in result:
            raise Exception(f"Baidu API error {result['error_code']}: {result['error_msg']}")

        # 4. Join translation results (preserve original text line structure)
        return '\n'.join(item['dst'] for item in result['trans_result'])

    except requests.exceptions.RequestException as e:
        raise Exception(f"Network request failed: {str(e)}")
    except json.JSONDecodeError:
        raise Exception("Failed to parse Baidu API response")