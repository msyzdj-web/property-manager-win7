"""
缴费记录模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from models.database import Base


class Payment(Base):
    """缴费记录表"""
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    resident_id = Column(Integer, ForeignKey('residents.id'), nullable=False, comment='住户ID')
    charge_item_id = Column(Integer, ForeignKey('charge_items.id'), nullable=False, comment='收费项目ID')
    period = Column(String(20), nullable=False, comment='缴费周期，格式：YYYY-MM')
    billing_start_date = Column(DateTime, nullable=False, comment='计费开始日期')
    billing_end_date = Column(DateTime, nullable=False, comment='计费结束日期')
    billing_months = Column(Integer, nullable=False, default=1, comment='计费周期数（月数）')
    paid_months = Column(Integer, default=0, comment='已缴费周期数（月数）')
    amount = Column(Numeric(10, 2), nullable=False, comment='总金额（全部计费周期的金额）')
    paid_amount = Column(Numeric(10, 2), default=0, comment='已缴费金额')
    paid = Column(Integer, default=0, comment='缴费状态：1-已缴费，0-未缴费')
    paid_time = Column(DateTime, comment='缴费时间')
    operator = Column(String(50), comment='操作员')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    # 关联关系
    resident = relationship('Resident', backref='payments')
    charge_item = relationship('ChargeItem', backref='payments')
    transactions = relationship('PaymentTransaction', back_populates='payment', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, resident_id={self.resident_id}, period='{self.period}', paid={self.paid})>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'resident_id': self.resident_id,
            'resident_name': self.resident.name if self.resident else '',
            'resident_room_no': self.resident.room_no if self.resident else '',
            'charge_item_id': self.charge_item_id,
            'charge_item_name': self.charge_item.name if self.charge_item else '',
            'period': self.period,
            'billing_start_date': self.billing_start_date.strftime('%Y-%m-%d') if self.billing_start_date else '',
            'billing_end_date': self.billing_end_date.strftime('%Y-%m-%d') if self.billing_end_date else '',
            'billing_months': self.billing_months,
            'paid_months': self.paid_months,
            'amount': float(self.amount),
            'paid_amount': float(self.paid_amount) if self.paid_amount else 0.0,
            'paid': self.paid,
            'paid_status': '已缴费' if self.paid == 1 else f'部分缴费({self.paid_months}/{self.billing_months}月)' if self.paid_months > 0 else '未缴费',
            'paid_time': self.paid_time.strftime('%Y-%m-%d %H:%M:%S') if self.paid_time else '',
            'operator': self.operator or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

