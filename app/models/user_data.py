import os
import sqlite3
import logging

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'database.db')


def get_db_connection():
    """
    建立並回傳 SQLite 資料庫連線。
    預期資料庫路徑為 instance/database.db。
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"資料庫連線錯誤: {e}")
        return None


class UserModel:
    """使用者資料表操作方法"""

    @staticmethod
    def create(data):
        conn = get_db_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (?, ?, ?)",
                (data['username'], data['password_hash'], data.get('target_carbon_emission', 0))
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"UserModel.create 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        if not conn:
            return []

        try:
            return conn.execute('SELECT * FROM users').fetchall()
        except sqlite3.Error as e:
            logging.error(f"UserModel.get_all 錯誤: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_db_connection()
        if not conn:
            return None

        try:
            return conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        except sqlite3.Error as e:
            logging.error(f"UserModel.get_by_id 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_db_connection()
        if not conn:
            return None

        try:
            return conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        except sqlite3.Error as e:
            logging.error(f"UserModel.get_by_username 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update(user_id, data):
        conn = get_db_connection()
        if not conn:
            return False

        try:
            columns = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(user_id)
            conn.execute(f"UPDATE users SET {columns} WHERE id = ?", tuple(values))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"UserModel.update 錯誤: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_db_connection()
        if not conn:
            return False

        try:
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"UserModel.delete 錯誤: {e}")
            return False
        finally:
            conn.close()


class CarbonRecordModel:
    """碳排紀錄表操作方法"""

    @staticmethod
    def create(data):
        conn = get_db_connection()
        if not conn:
            return None

        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO carbon_records (user_id, category, action_name, parameter_value, carbon_amount, suggestion) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    data['user_id'],
                    data['category'],
                    data['action_name'],
                    data['parameter_value'],
                    data['carbon_amount'],
                    data.get('suggestion')
                )
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"CarbonRecordModel.create 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all(user_id=None):
        conn = get_db_connection()
        if not conn:
            return []

        try:
            if user_id is not None:
                return conn.execute('SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC', (user_id,)).fetchall()
            return conn.execute('SELECT * FROM carbon_records ORDER BY created_at DESC').fetchall()
        except sqlite3.Error as e:
            logging.error(f"CarbonRecordModel.get_all 錯誤: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        conn = get_db_connection()
        if not conn:
            return None

        try:
            return conn.execute('SELECT * FROM carbon_records WHERE id = ?', (record_id,)).fetchone()
        except sqlite3.Error as e:
            logging.error(f"CarbonRecordModel.get_by_id 錯誤: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        return CarbonRecordModel.get_all(user_id=user_id)

    @staticmethod
    def update(record_id, data):
        conn = get_db_connection()
        if not conn:
            return False

        if not data:
            return True

        try:
            columns = ', '.join([f"{key} = ?" for key in data.keys()])
            values = list(data.values())
            values.append(record_id)
            conn.execute(f"UPDATE carbon_records SET {columns} WHERE id = ?", tuple(values))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"CarbonRecordModel.update 錯誤: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(record_id):
        conn = get_db_connection()
        if not conn:
            return False

        try:
            conn.execute('DELETE FROM carbon_records WHERE id = ?', (record_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"CarbonRecordModel.delete 錯誤: {e}")
            return False
        finally:
            conn.close()
