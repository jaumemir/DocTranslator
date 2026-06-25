import os
from flask import current_app
from app.models.translate import Translate
from app.translate import word, excel, powerpoint, pdf,txt, csv_handle, md, html, to_translate


def main_wrapper(task_id, config, origin_path):
    """
    Translation task core logic
    :param task_id: Task ID
    :param origin_path: Original file absolute path
    :param target_path: Target file absolute path
    :param config: Translation configuration dictionary
    :return: Whether successful
    """
    try:
        # Get task object
        task = Translate.query.get(task_id)
        if not task:
            current_app.logger.error(f"Task {task_id} does not exist")
            return False

        # Initialize translation configuration (prompt-terminology loading)
        _init_translate_config(task)
        to_translate.init_openai(config['api_url'], config['api_key'])
        # Get file extension
        extension = os.path.splitext(origin_path)[1].lower()
        # Call file handler
        handler_map = {
            ('.docx', '.doc'): word,
            ('.xlsx', '.xls'): excel,
            ('.pptx', '.ppt'): powerpoint,
            ('.pdf',): pdf,
            ('.txt',): txt,
            ('.csv',): csv_handle,
            ('.md',): md,
            ('.html', '.htm'): html
        }

        # Find matching handler
        for ext_group, handler in handler_map.items():
            if extension in ext_group:

                status = handler.start(

                    trans=config  # Pass translation configuration
                )
                print('config settings', config)
                return status

        current_app.logger.error(f"Unsupported file type: {extension}")
        return False

    except Exception as e:
        current_app.logger.error(f"Translation task execution exception: {str(e)}", exc_info=True)
        return False


def pdf_handler(config, origin_path):
    pass
    # return gptpdf.start(config)
    # if pdf.is_scanned_pdf(origin_path):
    #     return gptpdf.start(config)
    # else:
    #     # 这里均使用gptpdf实现
    #     return gptpdf.start(config)
    #     # return pdf.start(config)


def _init_translate_config(trans):
    """
    Initialize translation configuration
    :param trans: Translation task object
    """
    # Set OpenAI API
    if trans.api_url and trans.api_key:
        set_openai_config(trans.api_url, trans.api_key)


def set_openai_config(api_url, api_key):
    """Set OpenAI API configuration"""
    import openai

    # Ensure URL ends with /v1/
    base_url = api_url
    if not base_url.endswith("/v1/"):
        if base_url.endswith("/v1"):
            # If ends with /v1, add /
            base_url = base_url + "/"
        elif base_url.endswith("/"):
            # If ends with /, add v1/
            base_url = base_url + "v1/"
        else:
            # If does not end with /, add /v1/
            base_url = base_url + "/v1/"

    openai.base_url = base_url
    openai.api_key = api_key


