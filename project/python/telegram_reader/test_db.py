import psycopg2

# 資料庫連線字串
db_url = "postgresql://postgres:postgres@postgres.default:5432/discovery_system"

try:
    # 建立連線
    conn = psycopg2.connect(db_url)
    print("連線成功！")

    # 建立 cursor 用於執行 SQL 查詢
    cursor = conn.cursor()

    # 執行一個簡單的查詢，這裡查詢 PostgreSQL 的版本
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print("PostgreSQL 版本:", version[0])

except Exception as e:
    print("連線失敗，錯誤訊息:", e)

finally:
    # 關閉 cursor 與連線
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals():
        conn.close()