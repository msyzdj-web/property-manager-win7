"""
数据库迁移脚本
自动检测并添加缺失的字段
"""
import sqlite3
import os
from datetime import datetime, timedelta
from models.database import DB_PATH


def migrate_database():
    """迁移数据库，添加缺失的字段"""
    if not os.path.exists(DB_PATH):
        print(f"数据库文件不存在: {DB_PATH}")
        print("程序首次运行时会自动创建数据库")
        return True
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查并添加 charge_items.unit 字段
        try:
            cursor.execute("SELECT unit FROM charge_items LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 charge_items.unit 字段...")
            cursor.execute("ALTER TABLE charge_items ADD COLUMN unit VARCHAR(20) DEFAULT '元/月'")
            # 更新现有记录
            cursor.execute("UPDATE charge_items SET unit = '元/月' WHERE unit IS NULL")
            print("✓ charge_items.unit 字段已添加")
        
        # 检查并添加 residents.move_in_date 字段
        try:
            cursor.execute("SELECT move_in_date FROM residents LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 residents.move_in_date 字段...")
            cursor.execute("ALTER TABLE residents ADD COLUMN move_in_date DATETIME")
            print("✓ residents.move_in_date 字段已添加")
        
        # 检查并添加 residents.identity 字段（房主/租户）
        try:
            cursor.execute("SELECT identity FROM residents LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 residents.identity 字段...")
            cursor.execute("ALTER TABLE residents ADD COLUMN identity VARCHAR(20) DEFAULT 'owner'")
            cursor.execute("UPDATE residents SET identity = 'owner' WHERE identity IS NULL")
            print("✓ residents.identity 字段已添加")
        
        # 检查并添加 residents.property_type 字段（住宅/商铺）
        try:
            cursor.execute("SELECT property_type FROM residents LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 residents.property_type 字段...")
            cursor.execute("ALTER TABLE residents ADD COLUMN property_type VARCHAR(20) DEFAULT 'residential'")
            cursor.execute("UPDATE residents SET property_type = 'residential' WHERE property_type IS NULL")
            print("✓ residents.property_type 字段已添加")
        
        # 检查并添加 residents.building 字段（楼栋）
        try:
            cursor.execute("SELECT building FROM residents LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 residents.building 字段...")
            cursor.execute("ALTER TABLE residents ADD COLUMN building VARCHAR(20)")
            cursor.execute("UPDATE residents SET building = '' WHERE building IS NULL")
            print("✓ residents.building 字段已添加")

        # 检查并添加 residents.unit 字段（单元）
        try:
            cursor.execute("SELECT unit FROM residents LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 residents.unit 字段...")
            cursor.execute("ALTER TABLE residents ADD COLUMN unit VARCHAR(20)")
            cursor.execute("UPDATE residents SET unit = '' WHERE unit IS NULL")
            print("✓ residents.unit 字段已添加")
        
        # 检查并添加 payments 表的新字段
        try:
            cursor.execute("SELECT billing_start_date FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 payments.billing_start_date 字段...")
            cursor.execute("ALTER TABLE payments ADD COLUMN billing_start_date DATETIME")
            print("✓ payments.billing_start_date 字段已添加")
        
        try:
            cursor.execute("SELECT billing_end_date FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 payments.billing_end_date 字段...")
            cursor.execute("ALTER TABLE payments ADD COLUMN billing_end_date DATETIME")
            print("✓ payments.billing_end_date 字段已添加")
        
        try:
            cursor.execute("SELECT billing_months FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 payments.billing_months 字段...")
            cursor.execute("ALTER TABLE payments ADD COLUMN billing_months INTEGER DEFAULT 1")
            # 更新现有记录
            cursor.execute("UPDATE payments SET billing_months = 1 WHERE billing_months IS NULL")
            print("✓ payments.billing_months 字段已添加")
        
        try:
            cursor.execute("SELECT paid_months FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 payments.paid_months 字段...")
            cursor.execute("ALTER TABLE payments ADD COLUMN paid_months INTEGER DEFAULT 0")
            # 更新现有记录
            cursor.execute("UPDATE payments SET paid_months = 0 WHERE paid_months IS NULL")
            print("✓ payments.paid_months 字段已添加")
        
        try:
            cursor.execute("SELECT paid_amount FROM payments LIMIT 1")
        except sqlite3.OperationalError:
            print("添加 payments.paid_amount 字段...")
            cursor.execute("ALTER TABLE payments ADD COLUMN paid_amount NUMERIC(10, 2) DEFAULT 0")
            # 更新现有记录：如果已缴费，设置paid_amount等于amount
            cursor.execute("UPDATE payments SET paid_amount = amount WHERE paid = 1 AND paid_amount IS NULL")
            cursor.execute("UPDATE payments SET paid_amount = 0 WHERE paid_amount IS NULL")
            print("✓ payments.paid_amount 字段已添加")
        
        # 为现有payments记录设置默认的计费日期（基于period字段）
        cursor.execute("""
            SELECT id, period FROM payments 
            WHERE billing_start_date IS NULL OR billing_end_date IS NULL
        """)
        records = cursor.fetchall()
        if records:
            print(f"更新 {len(records)} 条现有记录的计费日期...")
            for record_id, period in records:
                try:
                    # 解析period (格式: YYYY-MM)
                    year, month = map(int, period.split('-'))
                    start_date = datetime(year, month, 1)
                    # 结束日期为当月最后一天
                    if month == 12:
                        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
                    
                    cursor.execute("""
                        UPDATE payments 
                        SET billing_start_date = ?, 
                            billing_end_date = ?,
                            billing_months = 1
                        WHERE id = ?
                    """, (start_date, end_date, record_id))
                except:
                    # 如果解析失败，使用当前日期
                    now = datetime.now()
                    cursor.execute("""
                        UPDATE payments 
                        SET billing_start_date = ?, 
                            billing_end_date = ?,
                            billing_months = 1
                        WHERE id = ?
                    """, (now, now, record_id))
            print("✓ 现有记录的计费日期已更新")
        
        # 重新计算并修正所有 payments 的 billing_months（以 billing_start_date/billing_end_date 为准）
        try:
            cursor.execute("SELECT id, billing_start_date, billing_end_date, billing_months FROM payments")
            all_payments = cursor.fetchall()
            for pid, bstart, bend, bm in all_payments:
                if not bstart or not bend:
                    continue
                try:
                    # SQLite stores DATETIME as text; let sqlite parse via substrings
                    # We'll use Python to parse via sqlite3 returning string; use sqlite to get raw and let Python parse
                    import datetime as _dt
                    start = _dt.datetime.fromisoformat(bstart) if isinstance(bstart, str) else _dt.datetime(*bstart)
                    end = _dt.datetime.fromisoformat(bend) if isinstance(bend, str) else _dt.datetime(*bend)
                    months = (end.year - start.year) * 12 + (end.month - start.month)
                    if end.day >= start.day:
                        months += 1
                    if months <= 0:
                        months = 1
                    if bm != months:
                        cursor.execute("UPDATE payments SET billing_months = ? WHERE id = ?", (months, pid))
                except Exception:
                    continue
            print("✓ 所有 payments 的 billing_months 已按计费日期重新计算并修正")
            conn.commit()
        except Exception:
            conn.rollback()
        # 确保 payment_transactions 表存在
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER NOT NULL,
                    amount NUMERIC(10,2) NOT NULL,
                    paid_time DATETIME,
                    operator VARCHAR(50),
                    created_at DATETIME DEFAULT (datetime('now'))
                )
            """)
            print("✓ payment_transactions 表已存在或创建完成")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"创建 payment_transactions 表失败：{e}")
        
        # 确保 print_logs 表存在（记录打印流水）
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS print_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payment_id INTEGER,
                    seq INTEGER NOT NULL,
                    printed_at DATETIME DEFAULT (datetime('now'))
                )
            """)
            print("✓ print_logs 表已存在或创建完成")
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"创建 print_logs 表失败：{e}")
        
        conn.commit()
        print("\n数据库迁移完成！")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n数据库迁移失败: {str(e)}")
        return False
    finally:
        conn.close()


if __name__ == '__main__':
    print("=" * 50)
    print("数据库迁移工具")
    print("=" * 50)
    print()
    migrate_database()
    print()
    input("按回车键退出...")

