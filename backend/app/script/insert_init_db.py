from datetime import date
from sqlalchemy import text, inspect
from app import db
from app.models.prompt import Prompt
from app.models.user import User


# 定义初始化数据
INITIAL_PROMPTS = [
    {
        "title": "小说翻译专家",
        "content": "You are a highly skilled translation engine with expertise in fiction literature, known as the 'Fiction Translation Expert.' Your function is to translate texts into {target_lang}, focusing on enhancing the narrative and emotional depth of fiction translations. Ensure every word captures the essence of the original work, providing nuanced and faithful renditions of novels, short stories, and other narrative forms. Use your expertise to translate fiction into the target language with enhanced emotional resonance and cultural relevance. Maintain the original storytelling elements and cultural references without adding any explanations or annotations.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "电商翻译大师",
        "content": "You are a highly skilled translation engine with expertise in the e-commerce sector, known as the 'E-commerce Expert.' Your function is to translate texts accurately into {target_lang}, ensuring that product descriptions, customer reviews, and e-commerce articles resonate with online shoppers. Carefully designed prompts ensure translations are both precise and culturally relevant, enhancing the shopping experience. Maintain the original tone and information without adding any explanations or annotations.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "金融领域翻译专家",
        "content": "You are a highly skilled translation engine with expertise in the financial sector, known as the 'Financial Expert.' Your function is to translate texts accurately into {target_lang}, maintaining the original format, financial terms, market data, and currency abbreviations. Carefully designed prompts ensure translations are both precise and professional, tailored for financial articles and reports. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "GitHub 翻译增强器",
        "content": "You are a sophisticated translation engine with expertise in GitHub content, known as the 'GitHub Translation Enhancer.' Your function is to translate texts accurately into {target_lang}, preserving technical terms, code snippets, markdown formatting, and platform-specific language. Carefully designed prompts ensure translations are both precise and contextually appropriate, tailored for GitHub repositories, issues, pull requests, and comments. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "法律领域翻译专家",
        "customer_id": 0,
        "share_flag": "Y",  # 默认共享状态
        "content": "You are a highly skilled translation engine with expertise in the legal sector, known as the 'Legal Expert.' Your function is to translate texts accurately into {target_lang}, maintaining the original format, legal terminology, references, and abbreviations. Carefully designed prompts ensure translations are both precise and professional, tailored for legal documents, articles, and reports. Do not add any explanations or annotations to the translated text."
    },
    {
        "title": "医学领域翻译专家",
        "content": "You are a highly skilled translation engine with expertise in the medical sector, known as the 'Medical Expert.' Your function is to translate texts accurately into {target_lang}, maintaining the original format, medical terms, and abbreviations. Carefully designed prompts ensure translations are both precise and professional, tailored for medical articles, reports, and documents. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "新闻媒体译者",
        "content": "You are a highly skilled translation engine with expertise in the news media sector, known as the 'Media Expert.' Your function is to translate texts accurately into {target_lang}, preserving the nuances, tone, and style of journalistic writing. Carefully designed prompts ensure translations are both precise and contextually appropriate, tailored for news articles, reports, and media content. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "学术论文翻译大师",
        "content": "You are a highly skilled translation engine with expertise in academic paper translation, known as the 'Academic Paper Translation Expert.' Your function is to translate academic texts accurately into {target_lang}, ensuring the precise translation of complex concepts and specialized terminology while preserving the original academic tone. Carefully designed prompts ensure translations are both scholarly and contextually appropriate, tailored for journals, research papers, and scholarly articles across various disciplines. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    {
        "title": "科技类翻译大师",
        "content": "You are a highly skilled translation engine with expertise in the technology sector, known as the 'Technology Expert.' Your function is to translate texts accurately into {target_lang}, maintaining the original format, technical terms, and abbreviations. Carefully designed prompts ensure translations are both precise and professional, tailored for technology articles, reports, and documents. Do not add any explanations or annotations to the translated text.",
        "customer_id": 0,
        "share_flag": "Y"  # 默认共享状态
    },
    # {
    #     "title": "生活翻译专家",
    #     "content": "",
    #     "customer_id": 0,
    #     "share_flag": "Y"  # 默认共享状态
    # },
    # {
    #     "title": "生活翻译专家",
    #     "content": "",
    #     "customer_id": 0,
    #     "share_flag": "Y"  # 默认共享状态
    # }
]


# Insert initial prompt table data (avoid duplicates)
def insert_initial_data(app):
    with app.app_context():
        for prompt_data in INITIAL_PROMPTS:
            # Check if identical data already exists
            if not Prompt.query.filter_by(
                    title=prompt_data["title"],
                    content=prompt_data["content"],
                    customer_id=prompt_data["customer_id"]
            ).first():
                # Create new data
                prompt = Prompt(
                    title=prompt_data["title"],
                    content=prompt_data["content"],
                    customer_id=prompt_data["customer_id"],
                    share_flag=prompt_data["share_flag"],  # Default sharing status
                    created_at=date.today()  # Auto set current time
                )
                db.session.add(prompt)
        # Set prompt_fav table id to auto increment, execute ALTER TABLE statement
        # db.session.execute(text("ALTER TABLE prompt_fav MODIFY COLUMN id BIGINT AUTO_INCREMENT;"))
        # Commit transaction
        db.session.commit()
        print("✅ Initial data completed!")




def is_auto_increment(table_name, column_name):
    """Check if specified field in specified table is already auto increment"""
    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    column = next((col for col in columns if col["name"] == column_name), None)
    if not column:
        return False
    return column.get("autoincrement", False)

def set_auto_increment(app):
    with app.app_context():
        # Get database dialect
        dialect = db.engine.dialect.name
        # Check if id field is already auto increment
        if is_auto_increment("prompt_fav", "id"):
            print("✅ 'id' field is already auto increment (no modification needed)")
            return

        if dialect == "mysql":
            sql = "ALTER TABLE prompt_fav MODIFY COLUMN id BIGINT AUTO_INCREMENT;"
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print("✅ 'id' field set to auto increment (MySQL)")
            except Exception as e:
                db.session.rollback()
                print(f"❌ Failed to set auto increment: {e}")
        elif dialect == "sqlite":
            # SQLite sets id field to auto increment by rebuilding table
            try:
                with db.engine.begin() as connection:
                    # 1. Create new table
                    connection.execute(text("""
                        CREATE TABLE prompt_fav_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            prompt_id INTEGER NOT NULL,
                            customer_id INTEGER NOT NULL,
                            created_at DATETIME,
                            updated_at DATETIME
                        );
                    """))
                    # 2. Copy data
                    connection.execute(text("""
                        INSERT INTO prompt_fav_new (prompt_id, customer_id, created_at, updated_at)
                        SELECT prompt_id, customer_id, created_at, updated_at FROM prompt_fav;
                    """))
                    # 3. Delete old table
                    connection.execute(text("DROP TABLE prompt_fav;"))
                    # 4. Rename new table
                    connection.execute(text("ALTER TABLE prompt_fav_new RENAME TO prompt_fav;"))
                print("✅ 'id' field set to auto increment (SQLite)")
            except Exception as e:
                print(f"❌ Failed to set auto increment: {e}")
        else:
            raise NotImplementedError(f"Unsupported database dialect: {dialect}")

# Initialize settings table
def insert_initial_settings(app):
    """Initialize system configuration table data"""
    INITIAL_SETTINGS = [
        {"id": 1, "alias": "notice_setting", "value": '["1"]', "serialized": 1,
         "created_at": "2024-06-25 01:39:39", "group": None},
        {"id": 2, "alias": "api_url", "value": "https://api.ezworkapi.top/v1",
         "serialized": 0,
         "created_at": "2024-07-26 05:26:21", "updated_at": "2025-04-14 03:53:53.066041",
         "group": "api_setting"},
        {"id": 3, "alias": "api_key", "value": "sk-xxxx", "serialized": 0,
         "created_at": "2024-07-26 05:26:21", "updated_at": "2025-04-14 03:53:53.070526",
         "group": "api_setting"},
        {"id": 4, "alias": "models", "value": "gpt-3.5-turbo-0125,deepseek-chat,test,666666666",
         "serialized": 0,
         "created_at": "2024-07-26 05:26:21", "updated_at": "2025-04-14 03:53:53.071734",
         "group": "api_setting"},
        {"id": 5, "alias": "default_model", "value": "", "serialized": 0,
         "created_at": "2024-07-26 05:26:21", "updated_at": "2025-04-14 03:53:53.072734",
         "group": "api_setting"},
        {"id": 6, "alias": "default_backup", "value": "deepseek-chat", "serialized": 0,
         "created_at": "2024-07-26 05:26:21", "updated_at": "2024-07-26 13:26:21",
         "group": "api_setting"},
        {"id": 7, "alias": "prompt", "value": "You are a document translation assistant. Please translate the following text, words, or phrases directly into {target_lang}, without returning the original text. If the text contains {target_lang} text, proper nouns (such as email addresses, brand names, unit nouns like mm, px, ℃, etc.), or untranslatable content, please return the original text directly without explanation. For untranslatable text, return the original content. Preserve extra spaces.", "serialized": 0,
         "created_at": "2024-09-02 05:55:30", "updated_at": "2024-09-02 13:55:30",
         "group": "other_setting"},
        {"id": 8, "alias": "threads", "value": "6", "serialized": 0,
         "created_at": "2024-09-02 05:55:30", "updated_at": "2025-04-14 03:54:26.467467",
         "group": "other_setting"},
        {"id": 9, "alias": "email_limit", "value": "", "serialized": 0,
         "created_at": "2024-09-02 05:55:31", "updated_at": "2024-09-02 13:55:31",
         "group": "other_setting"},
        {"id": 10, "alias": "version", "value": "community", "serialized": 0,
         "created_at": "2025-02-18 01:57:39", "updated_at": "2025-03-04 00:57:20.624926",
         "group": "site_setting"}
    ]

    with app.app_context():
        try:
            inserted_count = 0
            for setting in INITIAL_SETTINGS:
                # Composite check: verify both id and alias existence
                exists = db.session.execute(
                    text("SELECT 1 FROM setting WHERE id = :id OR alias = :alias"),
                    {"id": setting["id"], "alias": setting["alias"]}
                ).scalar()

                if not exists:
                    # Build dynamic SQL (handle potentially NULL updated_at and group)
                    sql = """
                    INSERT INTO setting (
                        id, alias, value, serialized, created_at,
                        updated_at, deleted_flag, `group`
                    ) VALUES (
                        :id, :alias, :value, :serialized, :created_at,
                        :updated_at, 'N', :group
                    )
                    """
                    params = {
                        "id": setting["id"],
                        "alias": setting["alias"],
                        "value": setting["value"],
                        "serialized": setting["serialized"],
                        "created_at": setting["created_at"],
                        "updated_at": setting.get("updated_at"),
                        "group": setting.get("group")
                    }
                    db.session.execute(text(sql), params)
                    inserted_count += 1

            if inserted_count > 0:
                db.session.commit()
                print(f"✅ Successfully inserted {inserted_count}/{len(INITIAL_SETTINGS)} configurations")
            else:
                print("⏩ All system configuration data already exists, no insertion needed")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Initialization failed: {str(e)}")
            raise


# Initialize admin user
def insert_initial_admin(app):
    """Initialize admin user for both MySQL and SQLite"""
    INITIAL_ADMIN = {
        "id": 1,
        "name": "admin",
        "password": "123456",  # Plain text password (should be changed after first login)
        "email": "admin",
        "deleted_flag": "N"
    }

    with app.app_context():
        try:
            # Check if admin user already exists
            existing_admin = User.query.filter_by(id=INITIAL_ADMIN["id"]).first()
            if not existing_admin:
                # Create admin user
                admin = User(
                    id=INITIAL_ADMIN["id"],
                    name=INITIAL_ADMIN["name"],
                    password=INITIAL_ADMIN["password"],
                    email=INITIAL_ADMIN["email"],
                    deleted_flag=INITIAL_ADMIN["deleted_flag"]
                )
                db.session.add(admin)
                db.session.commit()
                print(f"✅ Admin user created successfully (email: {INITIAL_ADMIN['email']}, password: {INITIAL_ADMIN['password']})")
            else:
                print("⏩ Admin user already exists, no insertion needed")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Admin user initialization failed: {str(e)}")
            raise

