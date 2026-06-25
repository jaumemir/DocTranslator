import sqlite3
import os
import shutil

# 数据库文件路径
DB_PATH = r"\dev.db"

# 备份数据库文件路径
BACKUP_DB_PATH = r'\dev.db.backup'


def backup_database():
    """Backup database file"""
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' does not exist.")
        exit(1)
    shutil.copy(DB_PATH, BACKUP_DB_PATH)
    print(f"Database backed up to '{BACKUP_DB_PATH}'.")


def add_column_if_not_exists(cursor, table_name, column_name, column_type, default_value=None):
    """Add column if it doesn't exist"""
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = [column[1] for column in cursor.fetchall()]
    if column_name not in columns:
        print(f"Adding column '{column_name}' to table '{table_name}'...")
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            alter_sql += f" DEFAULT {default_value}"
        cursor.execute(alter_sql)
    else:
        print(f"Column '{column_name}' already exists in table '{table_name}'. Skipping...")


def update_translate_size(cursor):
    """Update size field in Translate table"""
    cursor.execute("SELECT id, origin_filepath FROM translate;")
    translates = cursor.fetchall()
    for translate_id, origin_filepath in translates:
        if origin_filepath and os.path.exists(origin_filepath):
            file_size = os.path.getsize(origin_filepath)
            cursor.execute('''
                UPDATE translate SET size = ? WHERE id = ?;
            ''', (file_size, translate_id))
            print(f"Updated size for translate ID {translate_id}: {file_size} bytes")
        else:
            # Explicitly set size to 0
            cursor.execute('''
                UPDATE translate SET size = 0 WHERE id = ?;
            ''', (translate_id,))
            print(
                f"Warning: File not found for translate ID {translate_id}: {origin_filepath}. Set size to 0.")


def update_customer_total_storage(cursor):
    """Update total_storage field in Customer table"""
    cursor.execute('''
        UPDATE customer SET total_storage = 104857600;
    ''')
    print("Updated total_storage for all customers.")


def main():
    # Backup database
    backup_database()

    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Add columns (if not exist)
    add_column_if_not_exists(cursor, 'translate', 'size', 'BIGINT', default_value=0)
    add_column_if_not_exists(cursor, 'customer', 'total_storage', 'BIGINT', default_value=104857600)

    # Update data
    update_translate_size(cursor)
    update_customer_total_storage(cursor)

    # Commit changes and close connection
    conn.commit()
    conn.close()
    print("Database migration successful!")


if __name__ == "__main__":
    main()
