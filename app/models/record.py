import sqlite3
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'instance', 'database.db')
DATABASE_URL = os.environ.get('DATABASE_URL')

IS_POSTGRES = DATABASE_URL is not None


def get_db():
    """Get database connection - PostgreSQL on Railway, SQLite locally."""
    try:
        if IS_POSTGRES:
            return psycopg2.connect(DATABASE_URL)
        else:
            conn = sqlite3.connect(DATABASE)
            conn.row_factory = sqlite3.Row
            return conn
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return None


class CarbonRecord:
    @staticmethod
    def create(user_id, category, action_name, parameter_value, carbon_amount, suggestion=""):
        conn = get_db()
        if not conn:
            return None
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO carbon_records (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
                       VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                    (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
                )
                record_id = cur.fetchone()[0]
            else:
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO carbon_records (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, category, action_name, parameter_value, carbon_amount, suggestion)
                )
                record_id = cur.lastrowid
            conn.commit()
            return record_id
        except Exception as e:
            logging.error(f"CarbonRecord.create error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(record_id):
        conn = get_db()
        if not conn:
            return None
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM carbon_records WHERE id = %s", (record_id,))
                record = cur.fetchone()
                return dict(record) if record else None
            else:
                record = conn.execute("SELECT * FROM carbon_records WHERE id = ?", (record_id,)).fetchone()
                return dict(record) if record else None
        except Exception as e:
            logging.error(f"CarbonRecord.get_by_id error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all_by_user(user_id):
        conn = get_db()
        if not conn:
            return []
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM carbon_records WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
                records = cur.fetchall()
                return [dict(r) for r in records]
            else:
                records = conn.execute("SELECT * FROM carbon_records WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
                return [dict(r) for r in records]
        except Exception as e:
            logging.error(f"CarbonRecord.get_all_by_user error: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def delete(record_id):
        conn = get_db()
        if not conn:
            return False
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor()
                cur.execute("DELETE FROM carbon_records WHERE id = %s", (record_id,))
            else:
                conn.execute("DELETE FROM carbon_records WHERE id = ?", (record_id,))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"CarbonRecord.delete error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
