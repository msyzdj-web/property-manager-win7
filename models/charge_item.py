"""
收费项目模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from models.database import Base


class ChargeItem(Base):
    """收费项目表"""
    __tablename__ = 'charge_items'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, comment='项目名称')
    price = Column(Numeric(10, 2), nullable=False, comment='单价/固定金额')
    charge_type = Column(String(20), nullable=False, comment='收费类型：fixed-固定，area-按面积，manual-手动')
    unit = Column(String(20), default='元/月', comment='单位：如 元/月、元/年、元/平方米等')
    status = Column(Integer, default=1, comment='状态：1-启用，0-停用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def __repr__(self):
        return f"<ChargeItem(id={self.id}, name='{self.name}', type='{self.charge_type}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'charge_type': self.charge_type,
            'charge_type_name': self.get_charge_type_name(),
            'unit': self.unit or '元/月',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
    
    def get_charge_type_name(self):
        """获取收费类型名称"""
        type_map = {
            'fixed': '固定',
            'area': '按面积',
            'manual': '手动'
        }
        return type_map.get(self.charge_type, self.charge_type)

