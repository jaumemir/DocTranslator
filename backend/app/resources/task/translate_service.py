import logging
import os
from datetime import datetime
from threading import Thread
from flask import current_app
from app.models.translate import Translate
from app.extensions import db
from .main import main_wrapper
from ...models.comparison import Comparison
from ...models.prompt import Prompt
import pytz


class TranslateEngine:
    def __init__(self, task_id):
        self.task_id = task_id
        self.app = current_app._get_current_object()  # Get real app object

    def execute(self):
        """Start translation task entry point"""
        try:
            # Prepare task in main thread context
            with self.app.app_context():
                task = self._prepare_task()

            # Pass real app object and task ID when starting thread
            thr = Thread(
                target=self._async_wrapper,
                args=(self.app, self.task_id)
            )
            thr.start()
            return True
        except Exception as e:
            self.app.logger.error(f"Task initialization failed: {str(e)}", exc_info=True)
            return False

    def _async_wrapper(self, app, task_id):
        """Async execution wrapper"""
        with app.app_context():
            from app.extensions import db  # Ensure import in each thread
            try:
                # Get task object using new session
                task = db.session.query(Translate).get(task_id)
                if not task:
                    app.logger.error(f"Task {task_id} does not exist")
                    return

                # Execute core logic
                success = self._execute_core(task)
                self._complete_task(success)
            except Exception as e:
                app.logger.error(f"Task execution exception: {str(e)}", exc_info=True)
                self._complete_task(False)
            finally:
                db.session.remove()  # Clean up thread-local session

    def _execute_core(self, task):
        """Execute core translation logic"""
        try:
            # Initialize translation configuration
            self._init_translate_config(task)

            # Build trans dictionary as required
            trans_config = self._build_trans_config(task)

            # Call main_wrapper to execute translation
            return main_wrapper(task_id=task.id, config=trans_config,
                                origin_path=task.origin_filepath)
        except Exception as e:
            current_app.logger.error(f"Translation execution failed: {str(e)}", exc_info=True)
            return False

    def _prepare_task(self):
        """Prepare translation task"""
        task = Translate.query.get(self.task_id)
        if not task:
            raise ValueError(f"Task {self.task_id} does not exist")

        # Verify file exists
        if not os.path.exists(task.origin_filepath):
            raise FileNotFoundError(f"Original file does not exist: {task.origin_filepath}")

        # Update task status
        task.status = 'process'
        task.start_at = datetime.now(pytz.timezone(self.app.config['TIMEZONE']))  # Use configured timezone
        db.session.commit()
        return task

    def _build_trans_config(self, task):
        """Build trans dictionary as required by file handlers"""
        config = {
            'id': task.id,  # 任务ID
            'target_lang': task.lang,
            'uuid': task.uuid,
            'target_path_dir': os.path.dirname(task.target_filepath),
            'threads': task.threads,
            'file_path': task.origin_filepath,
            'target_file': task.target_filepath,
            'api_url': task.api_url,
            'api_key': task.api_key,
            # 机器翻译相关
            'app_id': task.app_id,
            'app_key': task.app_key,
            'type': task.type,
            'lang': task.lang,
            'server': task.server,
            'run_complete': True,
            'model': task.model,
            'backup_model': task.backup_model,
            'comparison_id': task.comparison_id,
            'prompt_id': task.prompt_id,
            'prompt': self._get_final_prompt(task),
            'terms_dict': self._get_matched_terms(task) if task.comparison_id else None,
            'use_baidu_terms': self._should_use_baidu_terms(task),
            'extension': os.path.splitext(task.origin_filepath)[1]

        }

        return config

    def _get_final_prompt(self, task):
        """
        Get final prompt
        Prioritize using template from prompt_id, otherwise use task.prompt
        """
        # If has prompt_id, query database
        if task.prompt_id and task.prompt_id != 0:
            try:
                prompt_obj = db.session.query(Prompt).filter_by(id=task.prompt_id).first()
                if prompt_obj and prompt_obj.content:
                    logging.info(f"[Task{task.id}] Using prompt template ID: {task.prompt_id}")
                    return prompt_obj.content
                else:
                    logging.warning(
                        f"[Task{task.id}] Prompt template ID {task.prompt_id} does not exist or is empty")
            except Exception as e:
                logging.error(f"[Task{task.id}] Failed to get prompt template: {e}")

        # Use prompt from task
        prompt = task.prompt or "Please translate the following text to {target_lang}, maintaining the original format and style:"

        logging.info(f"[Task{task.id}] Using task's built-in prompt")
        return prompt

    def _get_matched_terms(self, task):
        """
        Get terminology content (for AI translation dynamic matching)
        Return parsed term pair list
        """
        if not task.comparison_id or task.comparison_id == 0:
            logging.info(f"[Task{task.id}] No terminology ID set")
            return None

        logging.info(f"[Task{task.id}] Starting to query terminology ID: {task.comparison_id}")

        try:
            # Add more detailed query conditions, ensure not deleted
            comparison = db.session.query(Comparison).filter(
                Comparison.id == task.comparison_id,
                Comparison.deleted_flag == 'N'
            ).first()

            if not comparison:
                logging.warning(f"[Task{task.id}] Terminology ID {task.comparison_id} does not exist or is deleted")
                return None

            if not comparison.content or comparison.content.strip() == '':
                logging.warning(f"[Task{task.id}] Terminology ID {task.comparison_id} content is empty")
                return None

            logging.info(
                f"[Task{task.id}] Found terminology: {comparison.title}, content length: {len(comparison.content)}")

            # Parse terminology content
            terms_content = comparison.content.strip()
            term_pairs = []

            # Support multiple separators
            separator = ';'
            if ';' not in terms_content:
                if '\n' in terms_content:
                    separator = '\n'
                elif '|' in terms_content:
                    separator = '|'

            for term_pair in terms_content.split(separator):
                term_pair = term_pair.strip()
                if not term_pair:
                    continue

                # Support multiple formats: comma, tab, colon
                if ',' in term_pair:
                    parts = term_pair.split(',', 1)
                elif '\t' in term_pair:
                    parts = term_pair.split('\t', 1)
                elif ':' in term_pair:
                    parts = term_pair.split(':', 1)
                else:
                    continue

                if len(parts) != 2:
                    continue

                source_term = parts[0].strip()
                target_term = parts[1].strip()

                if source_term and target_term:
                    term_pairs.append({
                        'source': source_term,
                        'target': target_term
                    })

            if term_pairs:
                logging.info(f"[Task{task.id}] Successfully parsed terminology, total {len(term_pairs)} term pairs")
                # Print first few term pairs as example
                sample = term_pairs[:3]
                for i, pair in enumerate(sample):
                    logging.info(
                        f"[Task{task.id}] Term example{i + 1}: {pair['source']} → {pair['target']}")
                return term_pairs
            else:
                logging.warning(
                    f"[Task{task.id}] Terminology is empty after parsing, original content: {terms_content[:100]}...")
                return None

        except Exception as e:
            logging.error(f"[Task{task.id}] Failed to get terminology: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _should_use_baidu_terms(self, task):
        """
        Determine if Baidu translation should enable terminology
        """
        if task.server != 'baidu':
            return False

        # Baidu translation: comparison_id=1 means enable terminology
        return task.comparison_id == 1

    def _init_translate_config(self, task):
        """Initialize translation configuration"""
        if task.api_url and task.api_key:
            import openai
            openai.api_base = task.api_url
            openai.api_key = task.api_key

    def _complete_task(self, success):
        """Update task status"""
        try:
            task = db.session.query(Translate).get(self.task_id)
            if task:
                task.status = 'done' if success else 'failed'
                task.end_at = datetime.now(pytz.timezone(self.app.config['TIMEZONE']))  # Use configured timezone
                task.process = 100.00 if success else 0.00
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            self.app.logger.error(f"Status update failed: {str(e)}", exc_info=True)


