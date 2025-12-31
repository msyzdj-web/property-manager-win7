"""
打印流水服务：提供当日序号查询与打印记录创建功能
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.print_log import PrintLog
from models.database import SessionLocal


class PrintService:
    @staticmethod
    def get_today_sequence(db: Session = None) -> int:
        """返回今天的下一个序号（count + 1）"""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            now = datetime.now()
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)
            count = db.query(func.count(PrintLog.id)).filter(
                PrintLog.printed_at >= start,
                PrintLog.printed_at < end
            ).scalar()
            return int(count or 0) + 1
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def create_print_log(payment_id: int = None, seq: int = None, db: Session = None) -> PrintLog:
        """创建打印记录；如果未提供 seq 则自动使用当天序号"""
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            if seq is None:
                seq = PrintService.get_today_sequence(db=db)
            pl = PrintLog(payment_id=payment_id, seq=seq)
            db.add(pl)
            db.commit()
            db.refresh(pl)
            return pl
        except Exception:
            db.rollback()
            raise
        finally:
            if close_db and db is not None:
                db.close()


