import os
import json
import hashlib
import datetime
from datetime import datetime as dt
import mysql.connector
from mysql.connector import errorcode

# Configure for XAMPP / local MySQL
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASS = os.getenv("MYSQL_PASS", "")           # set if you changed it
MYSQL_DB   = os.getenv("MYSQL_DB", "happyfood_db")

def get_conn(create_db_if_missing=True):
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASS,
            database=MYSQL_DB
        )
        return conn
    except mysql.connector.Error as err:
        if getattr(err, "errno", None) == errorcode.ER_BAD_DB_ERROR and create_db_if_missing:
            tmp = mysql.connector.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASS)
            tmp.autocommit = True
            cur = tmp.cursor()
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}` DEFAULT CHARACTER SET 'utf8mb4'")
            cur.close()
            tmp.close()
            conn = mysql.connector.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASS,
                database=MYSQL_DB
            )
            init_db(conn)
            return conn
        raise

def init_db(conn=None):
    close_after = False
    if conn is None:
        conn = get_conn(create_db_if_missing=True)
        close_after = True

    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS menus (
        id INT AUTO_INCREMENT PRIMARY KEY,
        category VARCHAR(64) NOT NULL,
        name VARCHAR(255) NOT NULL,
        price DECIMAL(10,2) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INT AUTO_INCREMENT PRIMARY KEY,
        items JSON NOT NULL,
        total DECIMAL(10,2) NOT NULL,
        status VARCHAR(32) NOT NULL,
        created_at DATETIME NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
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
    cur.execute("INSERT INTO menus (category, name, price) VALUES (%s, %s, %s)", (category, name, float(price)))
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
    return rows

def save_order(items_list, total):
    """
    items_list: list of dicts with at least:
      { "name": str, "unit_price": float, "qty": int, "size": "S"/"M"/"L", "subtotal": float }
    older tuple format still accepted (name, price) -> will be converted
    """
    payload = []
    for item in items_list:
        if isinstance(item, dict):
            payload.append({
                "name": item.get("name"),
                "unit_price": float(item.get("unit_price", item.get("price", 0))),
                "qty": int(item.get("qty", 1)),
                "size": item.get("size", "M"),
                "subtotal": float(item.get("subtotal", float(item.get("unit_price", item.get("price", 0))) * int(item.get("qty",1))))
            })
        else:
            # tuple/list (name, price)
            name, price = item
            payload.append({"name": name, "unit_price": float(price), "qty": 1, "size": "M", "subtotal": float(price)})
    items_json = json.dumps(payload, default=str)
    conn = get_conn()
    cur = conn.cursor()
    created = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("INSERT INTO orders (items, total, status, created_at) VALUES (%s, %s, %s, %s)",
                (items_json, float(total), "pending", created))
    conn.commit()
    cur.close()
    conn.close()

def get_pending_orders():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM orders WHERE status='pending' ORDER BY created_at")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for r in rows:
        try:
            r["items"] = json.loads(r["items"]) if isinstance(r["items"], str) else r["items"]
        except Exception:
            r["items"] = str(r["items"])
    return rows

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

# -------------------------
# User (admin) helpers
# -------------------------
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

# Summary helpers for admin history
def _count_and_sum_query(start_dt: dt, end_dt: dt):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as total FROM orders WHERE created_at BETWEEN %s AND %s",
        (start_dt.strftime("%Y-%m-%d %H:%M:%S"), end_dt.strftime("%Y-%m-%d %H:%M:%S"))
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"count": int(row[0]), "total": float(row[1])}
    return {"count": 0, "total": 0.0}

def get_orders_summary():
    now = datetime.datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_start = today_start - datetime.timedelta(days=1)
    week_start = today_start - datetime.timedelta(days=7)
    month_start = today_start - datetime.timedelta(days=30)
    year_start = today_start - datetime.timedelta(days=365)
    return {
        "today": _count_and_sum_query(today_start, now),
        "yesterday": _count_and_sum_query(yesterday_start, today_start),
        "week": _count_and_sum_query(week_start, now),
        "month": _count_and_sum_query(month_start, now),
        "year": _count_and_sum_query(year_start, now),
    }