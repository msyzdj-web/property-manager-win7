"""
付款流水服务
"""
from sqlalchemy.orm import Session
from models.payment_transaction import PaymentTransaction
from models.database import SessionLocal


class PaymentTransactionService:
    @staticmethod
    def create_transaction(payment_id: int, amount: float, operator: str = '', db: Session = None):
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        try:
            tx = PaymentTransaction(payment_id=payment_id, amount=amount, operator=operator)
            db.add(tx)
            # do not commit here if caller will commit; caller may pass same session
            if close_db:
                db.commit()
                db.refresh(tx)
            return tx
        except Exception as e:
            if close_db:
                db.rollback()
            raise
        finally:
            if close_db:
                db.close()

    @staticmethod
    def get_transactions_by_payment(payment_id: int, db: Session = None):
        """返回指定 payment 的所有流水，按时间升序"""
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        try:
            return db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).order_by(PaymentTransaction.paid_time.asc()).all()
        finally:
            if close_db:
                db.close()

    @staticmethod
    def get_last_transaction(payment_id: int, db: Session = None):
        """返回指定 payment 的最新一条流水"""
        if db is None:
            db = SessionLocal()
            close_db = True
        else:
            close_db = False
        try:
            return db.query(PaymentTransaction).filter(PaymentTransaction.payment_id == payment_id).order_by(PaymentTransaction.paid_time.desc()).first()
        finally:
            if close_db:
                db.close()


