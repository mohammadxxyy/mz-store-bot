import sqlite3
import random
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mz_store.db")


def get_connection() -> sqlite3.Connection:
    """إنشاء اتصال بقاعدة البيانات مع إرجاع الصفوف كقواميس"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """إنشاء جداول قاعدة بيانات متجر MZ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mz_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_code TEXT UNIQUE NOT NULL,
            user_id INTEGER,
            user_name TEXT,
            client_name TEXT,
            service_name TEXT,
            package_name TEXT,
            price TEXT,
            delivery_info TEXT,
            payment_method TEXT,
            status TEXT DEFAULT 'جديد - قيد التنفيذ والتسليم ⏳',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def generate_order_code() -> str:
    """توليد كود مميز لطلبات متجر MZ بصيغة MZ-XXXX"""
    random_num = random.randint(1000, 9999)
    return f"MZ-{random_num}"


def save_order(
    user_id: int,
    user_name: str,
    client_name: str,
    service_name: str,
    package_name: str,
    price: str,
    delivery_info: str,
    payment_method: str,
) -> str:
    """حفظ طلب جديد لمتجر MZ وإرجاع كود الطلب"""
    conn = get_connection()
    cursor = conn.cursor()
    order_code = generate_order_code()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        """
        INSERT INTO mz_orders (
            order_code, user_id, user_name, client_name,
            service_name, package_name, price,
            delivery_info, payment_method, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order_code,
            user_id,
            user_name,
            client_name,
            service_name,
            package_name,
            price,
            delivery_info,
            payment_method,
            created_at,
        ),
    )
    conn.commit()
    conn.close()
    return order_code


def get_order_by_code(order_code: str) -> Optional[Dict[str, Any]]:
    """جلب تفاصيل طلب معين بالكود"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM mz_orders WHERE UPPER(order_code) = UPPER(?)", (order_code.strip(),))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_orders_by_user(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    """جلب قائمة طلبات مستخدم معين"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM mz_orders WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_order_status(order_code: str, new_status: str) -> bool:
    """تحديث حالة طلب معين في متجر MZ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE mz_orders SET status = ? WHERE UPPER(order_code) = UPPER(?)",
        (new_status, order_code.strip()),
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def get_stats() -> Dict[str, Any]:
    """إحصائيات متجر MZ الرقمي"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM mz_orders")
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(DISTINCT user_id) as users FROM mz_orders")
    users = cursor.fetchone()["users"]

    cursor.execute("SELECT COUNT(*) as delivered FROM mz_orders WHERE status LIKE '%تم التسليم%'")
    delivered = cursor.fetchone()["delivered"]

    conn.close()
    return {
        "total_orders": total,
        "total_clients": users,
        "delivered_orders": delivered,
    }


# تهيئة الجداول فور استيراد الملف
init_db()
