import os
import json
import hashlib
from datetime import datetime as dt
import mysql.connector
from mysql.connector import errorcode

# Configure connection (adjust env or values if needed)
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASS = os.getenv("MYSQL_PASS", "")
MYSQL_DB   = os.getenv("MYSQL_DB", "happyfood_db")

def get_conn(create_db_if_missing=True):
    """
    Return a mysql.connector connection to MYSQL_DB.
    If database is missing and create_db_if_missing is True, create it.
    """
    try:
        return mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB,
            autocommit=False
        )
    except mysql.connector.Error as err:
        if create_db_if_missing and getattr(err, "errno", None) == errorcode.ER_BAD_DB_ERROR:
            # create database then reconnect
            tmp = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS)
            cur = tmp.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET 'utf8mb4'")
            cur.close()
            tmp.close()
            # now connect again
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASS,
                database=MYSQL_DB,
                autocommit=False
            )
            # ensure tables exist
            init_db(conn)
            return conn
        raise

def init_db(conn=None):
    """
    Create required tables if not present. If conn is None, open a connection.
    Also attempts to ensure 'items' column exists for orders.
    """
    close_after = False
    if conn is None:
        conn = get_conn(create_db_if_missing=True)
        close_after = True
    cur = conn.cursor()
    # menus table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menus (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(64) NOT NULL,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10,2) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    # orders table (items stored as JSON text)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        items JSON NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        status VARCHAR(32) NOT NULL,
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    # users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(128) NOT NULL,
        role VARCHAR(32) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    conn.commit()
    cur.close()
    if close_after:
        conn.close()

def add_menu_item(category, name, price):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO menus (category, name, price) VALUES (%s, %s, %s)",
                (category, name, float(price)))
    conn.commit()
    cur.close()
    conn.close()

def get_menus(category=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    if category and category != "Recommended":
        cur.execute("SELECT * FROM menus WHERE category=%s ORDER BY name", (category,))
    else:
        cur.execute("SELECT * FROM menus ORDER BY category, name")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows or []

def save_order(items_list, total):
    """
    Save order and return inserted order id.
    items_list: list of dicts with keys at least: name, unit_price, qty, size, subtotal
    Returns int order id.
    """
    items_json = json.dumps(items_list, default=str, ensure_ascii=False)
    conn = get_conn()
    cur = conn.cursor()
    created = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO orders (items, total, status, created_at) VALUES (%s, %s, %s, %s)",
                (items_json, float(total), "pending", created))
    conn.commit()
    order_id = cur.lastrowid
    cur.close()
    conn.close()
    return int(order_id)

def get_pending_orders():
    """
    Return list of pending orders as dicts. Convert items JSON to Python structures.
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM orders WHERE status='pending' ORDER BY created_at")
    rows = cur.fetchall() or []
    cur.close()
    conn.close()
    # convert items column from JSON string to python objects
    out = []
    for r in rows:
        try:
            r["items"] = json.loads(r["items"]) if isinstance(r.get("items"), (str, bytes)) else r.get("items")
        except Exception:
            r["items"] = r.get("items")
        out.append(r)
    return out

def get_orders_summary():
    """
    Return summary used by admin UI:
      {
        total_orders, total_earnings, served_count, pending_count,
        today:{count,total}, yesterday:{count,total},
        week:{count,total}, month:{count,total}, year:{count,total},
        recent_orders: [...]
      }
    """
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        # overall stats
        cur.execute("""
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(total), 0) AS total_earnings,
                SUM(CASE WHEN status='served' THEN 1 ELSE 0 END) AS served_count,
                SUM(CASE WHEN status='pending' THEN 1 ELSE 0 END) AS pending_count
            FROM orders
        """)
        overall = cur.fetchone() or {}

        # time buckets
        def single_stats(where_clause, params=None):
            sql = f"SELECT COUNT(*) AS count, COALESCE(SUM(total),0) AS total FROM orders WHERE {where_clause}"
            cur.execute(sql, params or ())
            return cur.fetchone() or {"count": 0, "total": 0.0}

        today = single_stats("DATE(created_at)=CURDATE()")
        yesterday = single_stats("DATE(created_at)=DATE_SUB(CURDATE(), INTERVAL 1 DAY)")
        week = single_stats("created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)")
        month = single_stats("MONTH(created_at)=MONTH(CURDATE()) AND YEAR(created_at)=YEAR(CURDATE())")
        year = single_stats("YEAR(created_at)=YEAR(CURDATE())")

        # recent orders
        cur.execute("SELECT id, total, status, created_at FROM orders ORDER BY created_at DESC LIMIT 50")
        recent = cur.fetchall() or []
    finally:
        cur.close()
        conn.close()

    return {
        "total_orders": int(overall.get("total_orders", 0)),
        "total_earnings": float(overall.get("total_earnings", 0.0)),
        "served_count": int(overall.get("served_count", 0)),
        "pending_count": int(overall.get("pending_count", 0)),
        "today": {"count": int(today.get("count", 0)), "total": float(today.get("total", 0.0))},
        "yesterday": {"count": int(yesterday.get("count", 0)), "total": float(yesterday.get("total", 0.0))},
        "week": {"count": int(week.get("count", 0)), "total": float(week.get("total", 0.0))},
        "month": {"count": int(month.get("count", 0)), "total": float(month.get("total", 0.0))},
        "year": {"count": int(year.get("count", 0)), "total": float(year.get("total", 0.0))},
        "recent_orders": recent
    }

def mark_order_served(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE orders SET status=%s WHERE id=%s", ("served", int(order_id)))
    conn.commit()
    cur.close()
    conn.close()

def delete_order(order_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM orders WHERE id=%s", (int(order_id),))
    conn.commit()
    cur.close()
    conn.close()

# user helpers
def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_user(username: str, password: str, role: str = "admin"):
    conn = get_conn()
    cur = conn.cursor()
    pw_hash = _hash_password(password)
    try:
        cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                    (username, pw_hash, role))
        conn.commit()
    except mysql.connector.IntegrityError:
        # user exists
        pass
    finally:
        cur.close()
        conn.close()

def verify_user(username: str, password: str):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, password_hash, role FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        return None
    if _hash_password(password) == row["password_hash"]:
        return {"id": row["id"], "username": row["username"], "role": row["role"]}
    return None