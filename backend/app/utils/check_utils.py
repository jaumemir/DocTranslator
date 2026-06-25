# utils/ai_utils.py
import openai
from io import BytesIO
import fitz  # PyMuPDF
import logging


class AIChecker:
    @staticmethod
    def check_openai_connection(api_url: str, api_key: str, model: str, timeout: int = 30):
        """OpenAI connectivity test"""
        try:
            openai.api_key = api_key
            base_url = api_url

            # Ensure URL ends with /v1/
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

            # Send a simple chat request
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi"}],
                timeout=timeout
            )
            # Return connection success and response content
            print(f"OpenAI connection successful: {response}")
            return True, response.choices[0].message.content
        except Exception as e:
            logging.error(f"OpenAI connection test failed: {str(e)}")
            return False, str(e)


    @staticmethod
    def check_pdf_scanned(file_stream: BytesIO):
        """PDF scanned document detection"""
        try:
            file_stream.seek(0)
            doc = fitz.open(stream=file_stream.read(), filetype="pdf")
            pages_to_check = min(5, len(doc))

            for page_num in range(pages_to_check):
                page = doc[page_num]
                if page.get_text().strip():  # Found editable text
                    return False
                if page.get_images():  # Found images
                    return True
            return False
        except Exception as e:
            logging.error(f"PDF detection failed: {str(e)}")
            raise
