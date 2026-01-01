"""
住户管理服务
"""
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models.resident import Resident
from models.database import SessionLocal
from sqlalchemy import and_


class ResidentService:
    """住户管理服务类"""
    
    @staticmethod
    def get_all_residents(db: Session = None, active_only: bool = False):
        """获取所有住户"""
        if db is None:
            db = SessionLocal()
        try:
            query = db.query(Resident)
            if active_only:
                query = query.filter(Resident.status == 1)
            return query.order_by(Resident.room_no).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_resident_by_id(resident_id: int, db: Session = None):
        """根据ID获取住户"""
        if db is None:
            db = SessionLocal()
        try:
            return db.query(Resident).filter(Resident.id == resident_id).first()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_resident_by_room_no(room_no: str, db: Session = None):
        """根据房号获取住户"""
        if db is None:
            db = SessionLocal()
        try:
            return db.query(Resident).filter(Resident.room_no == room_no).first()
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def get_resident_by_triplet(building: str, unit: str, room_no: str, db: Session = None):
        """根据 (building, unit, room_no) 获取住户"""
        if db is None:
            db = SessionLocal()
        try:
            return db.query(Resident).filter(
                Resident.building == (building or ''),
                Resident.unit == (unit or ''),
                Resident.room_no == room_no
            ).first()
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def get_resident_by_triplet(building: str, unit: str, room_no: str, db: Session = None):
        """根据 (building, unit, room_no) 三元组获取住户（全部匹配）"""
        if db is None:
            db = SessionLocal()
        try:
            return db.query(Resident).filter(
                and_(
                    Resident.building == (building or ''),
                    Resident.unit == (unit or ''),
                    Resident.room_no == room_no
                )
            ).first()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def create_resident(building: str = '', unit: str = '', room_no: str = '', name: str = None, phone: str = '', area: float = 0.0, 
                       move_in_date=None, identity: str = 'owner', property_type: str = 'residential', db: Session = None):
        """创建住户"""
        if db is None:
            db = SessionLocal()
        try:
            # 检查 (楼栋, 单元, 房号) 是否已存在
            existing = ResidentService.get_resident_by_triplet(building, unit, room_no, db)
            if existing:
                raise ValueError(f"房号 {room_no} 在 {building}-{unit} 已存在")
            
            resident = Resident(
                building=building,
                unit=unit,
                room_no=room_no,
                name=name,
                phone=phone,
                area=area,
                move_in_date=move_in_date,
                identity=identity,
                property_type=property_type,
                status=1
            )
            db.add(resident)
            db.commit()
            # refresh by re-querying to avoid session persistence issues
            resident = db.query(Resident).filter(Resident.id == resident.id).first()
            return resident
        except IntegrityError:
            db.rollback()
            raise ValueError(f"房号 {room_no} 已存在")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def update_resident(resident_id: int, building: str = None, unit: str = None, room_no: str = None, name: str = None, 
                       phone: str = None, area: float = None, move_in_date=None, 
                       status: int = None, identity: str = None, property_type: str = None, db: Session = None):
        """更新住户信息"""
        if db is None:
            db = SessionLocal()
        try:
            resident = db.query(Resident).filter(Resident.id == resident_id).first()
            if not resident:
                raise ValueError("住户不存在")
            
            # 如果修改楼栋/单元/房号中的任意一项，检查三元组唯一性
            new_building = building if building is not None else resident.building
            new_unit = unit if unit is not None else resident.unit
            new_room_no = room_no if room_no is not None else resident.room_no
            if (new_building, new_unit, new_room_no) != (resident.building, resident.unit, resident.room_no):
                existing = ResidentService.get_resident_by_triplet(new_building, new_unit, new_room_no, db)
                if existing and existing.id != resident_id:
                    raise ValueError(f"房号 {new_room_no} 在 {new_building}-{new_unit} 已存在")
                resident.room_no = new_room_no
                resident.building = new_building
                resident.unit = new_unit
            
            if building is not None:
                resident.building = building
            if unit is not None:
                resident.unit = unit
            
            if name is not None:
                resident.name = name
            if phone is not None:
                resident.phone = phone
            if area is not None:
                resident.area = area
            if move_in_date is not None:
                resident.move_in_date = move_in_date
            if identity is not None:
                resident.identity = identity
            if property_type is not None:
                resident.property_type = property_type
            if status is not None:
                resident.status = status
            
            db.commit()
            # re-query to avoid detached instance issues
            resident = db.query(Resident).filter(Resident.id == resident_id).first()
            return resident
        except IntegrityError:
            db.rollback()
            raise ValueError(f"房号 {room_no} 已存在")
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def delete_resident(resident_id: int, db: Session = None):
        """删除住户"""
        if db is None:
            db = SessionLocal()
        try:
            resident = db.query(Resident).filter(Resident.id == resident_id).first()
            if not resident:
                raise ValueError("住户不存在")

            # 级联删除：先删除与该住户相关的所有 payment_transactions 与 payments，再删除住户本身
            from models.payment import Payment
            from models.payment_transaction import PaymentTransaction

            payments = db.query(Payment).filter(Payment.resident_id == resident_id).all()
            if payments:
                payment_ids = [p.id for p in payments if p.id is not None]
                if payment_ids:
                    # 删除支付流水（transaction）记录
                    db.query(PaymentTransaction).filter(PaymentTransaction.payment_id.in_(payment_ids)).delete(synchronize_session=False)
                # 删除 payments
                db.query(Payment).filter(Payment.resident_id == resident_id).delete(synchronize_session=False)

            # 最后删除住户
            db.delete(resident)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def search_residents(keyword: str, db: Session = None):
        """搜索住户（按房号或姓名）"""
        if db is None:
            db = SessionLocal()
        try:
            keyword = f"%{keyword}%"
            return db.query(Resident).filter(
                (Resident.room_no.like(keyword)) | (Resident.name.like(keyword))
            ).order_by(Resident.room_no).all()
        finally:
            if db is not None:
                db.close()

