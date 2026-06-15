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


class User:
    @staticmethod
    def create(username, password_hash, target_carbon_emission=0):
        conn = get_db()
        if not conn:
            return None
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (%s, %s, %s) RETURNING id",
                    (username, password_hash, target_carbon_emission)
                )
                user_id = cur.fetchone()[0]
            else:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO users (username, password_hash, target_carbon_emission) VALUES (?, ?, ?)",
                    (username, password_hash, target_carbon_emission)
                )
                user_id = cur.lastrowid
            conn.commit()
            return user_id
        except Exception as e:
            logging.error(f"User.create error: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_db()
        if not conn:
            return None
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                user = cur.fetchone()
                return dict(user) if user else None
            else:
                user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
                return dict(user) if user else None
        except Exception as e:
            logging.error(f"User.get_by_id error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_db()
        if not conn:
            return None
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                user = cur.fetchone()
                return dict(user) if user else None
            else:
                user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                return dict(user) if user else None
        except Exception as e:
            logging.error(f"User.get_by_username error: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def update_target(user_id, target_carbon_emission):
        conn = get_db()
        if not conn:
            return False
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE users SET target_carbon_emission = %s WHERE id = %s",
                    (target_carbon_emission, user_id)
                )
            else:
                conn.execute(
                    "UPDATE users SET target_carbon_emission = ? WHERE id = ?",
                    (target_carbon_emission, user_id)
                )
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"User.update_target error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def delete(user_id):
        conn = get_db()
        if not conn:
            return False
        
        try:
            if IS_POSTGRES:
                cur = conn.cursor()
                cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            else:
                conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            logging.error(f"User.delete error: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
        conn = get_db()
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
