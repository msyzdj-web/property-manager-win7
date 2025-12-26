"""
付款流水模型
每次实际收款都会写入此表，便于审计与明细导出
"""
from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, String, func
from sqlalchemy.orm import relationship
from models.database import Base


class PaymentTransaction(Base):
    __tablename__ = 'payment_transactions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=False, comment='缴费记录ID')
    amount = Column(Numeric(10, 2), nullable=False, comment='本次实收金额')
    paid_time = Column(DateTime, default=func.now(), comment='收款时间')
    operator = Column(String(50), comment='操作员')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')

    # 关联
    payment = relationship('Payment', back_populates='transactions')

    def __repr__(self):
        return f"<PaymentTransaction(id={self.id}, payment_id={self.payment_id}, amount={self.amount})>"


