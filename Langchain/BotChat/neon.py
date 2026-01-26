import psycopg2
from datetime import datetime

# --- HÀM KHỞI TẠO DATABASE (Chạy mỗi khi bật Bot) ---
def init_neon_db(postgres_url: str):
    """Tự động tạo bảng orders trên Neon nếu chưa có"""
    if not postgres_url:
        print(">>> ⚠️ Bỏ qua Neon: Không có POSTGRES_URL")
        return
        
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS orders (
        id SERIAL PRIMARY KEY,
        order_code VARCHAR(50) UNIQUE NOT NULL, -- Mã đơn
        customer_name TEXT,                     -- Tên khách
        phone VARCHAR(50),                      -- SĐT
        address TEXT,                           -- Địa chỉ
        items TEXT,                             -- Danh sách món
        total_amount INTEGER DEFAULT 0,         -- Tổng tiền
        status VARCHAR(20) DEFAULT 'PENDING',   -- Trạng thái
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    conn = None
    try:
        # Kết nối tới Neon
        conn = psycopg2.connect(postgres_url)
        cur = conn.cursor()
        cur.execute(create_table_sql)
        conn.commit()
        cur.close()
        print(">>> ✅ Đã kết nối thành công tới NEON PostgreSQL!")
    except Exception as e:
        print(f">>> ❌ Lỗi kết nối Neon: {e}")
    finally:
        if conn: conn.close()