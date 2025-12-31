"""
打印流水模型
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from models.database import Base


class PrintLog(Base):
    """打印流水记录"""
    __tablename__ = 'print_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(Integer, ForeignKey('payments.id'), nullable=True, comment='关联的缴费记录（可选）')
    seq = Column(Integer, nullable=False, comment='当日序号，从1开始')
    printed_at = Column(DateTime, default=func.now(), comment='打印时间')

    def __repr__(self):
        return f"<PrintLog(id={self.id}, payment_id={self.payment_id}, seq={self.seq}, printed_at={self.printed_at})>"


