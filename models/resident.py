"""
住户模型
"""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from models.database import Base


class Resident(Base):
    """住户表"""
    __tablename__ = 'residents'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    room_no = Column(String(50), unique=True, nullable=False, comment='房号')
    name = Column(String(100), nullable=False, comment='姓名')
    building = Column(String(20), comment='楼栋')
    unit = Column(String(20), comment='单元')
    phone = Column(String(20), comment='电话')
    area = Column(Numeric(10, 2), comment='面积')
    move_in_date = Column(DateTime, comment='入住日期')
    identity = Column(String(20), default='owner', comment='身份：owner-房主，renter-租户')
    property_type = Column(String(20), default='residential', comment='房屋类型：residential-住宅，commercial-商铺')
    status = Column(Integer, default=1, comment='状态：1-正常，0-停用')
    created_at = Column(DateTime, default=func.now(), comment='创建时间')
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment='更新时间')
    
    def __repr__(self):
        return f"<Resident(id={self.id}, room_no='{self.room_no}', name='{self.name}')>"
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'room_no': self.room_no,
            'building': self.building if hasattr(self, 'building') else '',
            'unit': self.unit if hasattr(self, 'unit') else '',
            'name': self.name,
            'phone': self.phone or '',
            'area': float(self.area) if self.area else 0.0,
            'move_in_date': self.move_in_date.strftime('%Y-%m-%d') if self.move_in_date else '',
            'property_type': self.property_type if hasattr(self, 'property_type') else 'residential',
            'identity': self.identity if hasattr(self, 'identity') else 'owner',
            'status': self.status,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else '',
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

    @property
    def full_room_no(self):
        """返回完整房号字符串，例如：'6-1-1204'。
        规则：按‘楼栋-单元-房号’拼接非空部分，若楼栋/单元缺失则自动跳过对应部分，始终返回字符串。
        例如：
          - building=6, unit=1, room_no=1204 -> '6-1-1204'
          - building='', unit=2, room_no=1002  -> '2-1002'
          - building=None, unit=None, room_no=1306 -> '1306'
        """
        parts = []
        b = getattr(self, 'building', None)
        u = getattr(self, 'unit', None)
        if b is not None and str(b).strip() != '':
            parts.append(str(b).strip())
        if u is not None and str(u).strip() != '':
            parts.append(str(u).strip())
        # 房号总是加入，保证非空输出
        parts.append(str(self.room_no).strip())
        return "-".join(parts)

