"""
收费项目管理服务
"""
from sqlalchemy.orm import Session
from models.charge_item import ChargeItem
from models.database import SessionLocal
from decimal import Decimal, ROUND_HALF_UP
import math


class ChargeService:
    """收费项目管理服务类"""
    
    @staticmethod
    def get_all_charge_items(db: Session = None, active_only: bool = False):
        """获取所有收费项目"""
        if db is None:
            db = SessionLocal()
        try:
            query = db.query(ChargeItem)
            if active_only:
                query = query.filter(ChargeItem.status == 1)
            return query.order_by(ChargeItem.name).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_charge_item_by_id(item_id: int, db: Session = None):
        """根据ID获取收费项目"""
        if db is None:
            db = SessionLocal()
        try:
            return db.query(ChargeItem).filter(ChargeItem.id == item_id).first()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def create_charge_item(name: str, price: float, charge_type: str, unit: str = '元/月', db: Session = None):
        """创建收费项目"""
        if db is None:
            db = SessionLocal()
        try:
            if charge_type not in ['fixed', 'area', 'manual']:
                raise ValueError("收费类型必须是 fixed、area 或 manual")
            
            charge_item = ChargeItem(
                name=name,
                price=price,
                charge_type=charge_type,
                unit=unit,
                status=1
            )
            db.add(charge_item)
            db.commit()
            db.refresh(charge_item)
            return charge_item
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def update_charge_item(item_id: int, name: str = None, price: float = None, 
                          charge_type: str = None, unit: str = None, status: int = None, db: Session = None):
        """更新收费项目"""
        if db is None:
            db = SessionLocal()
        try:
            charge_item = db.query(ChargeItem).filter(ChargeItem.id == item_id).first()
            if not charge_item:
                raise ValueError("收费项目不存在")
            
            if name is not None:
                charge_item.name = name
            if price is not None:
                charge_item.price = price
            if charge_type is not None:
                if charge_type not in ['fixed', 'area', 'manual']:
                    raise ValueError("收费类型必须是 fixed、area 或 manual")
                charge_item.charge_type = charge_type
            if unit is not None:
                charge_item.unit = unit
            if status is not None:
                charge_item.status = status
            
            db.commit()
            db.refresh(charge_item)
            return charge_item
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def delete_charge_item(item_id: int, db: Session = None):
        """删除收费项目"""
        if db is None:
            db = SessionLocal()
        try:
            charge_item = db.query(ChargeItem).filter(ChargeItem.id == item_id).first()
            if not charge_item:
                raise ValueError("收费项目不存在")
            
            # 检查是否有缴费记录
            from models.payment import Payment
            payment_count = db.query(Payment).filter(Payment.charge_item_id == item_id).count()
            if payment_count > 0:
                raise ValueError(f"该收费项目有 {payment_count} 条缴费记录，无法删除")
            
            db.delete(charge_item)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def calculate_amount(charge_item: ChargeItem, resident_area: float = 0.0, 
                        months: int = 1, manual_amount: float = 0.0,
                        billing_start_date=None, billing_end_date=None, usage: float = None):
        """计算费用金额
        
        Args:
            charge_item: 收费项目
            resident_area: 住户面积（用于按面积计算）
            months: 计费周期数（月数），默认为1
            manual_amount: 手动输入金额（用于手动类型）
        
        Returns:
            计算后的金额
        """
        unit = (charge_item.unit or '').lower()
        price = float(charge_item.price)
        # 辅助：将浮点值四舍五入到整数元并返回 int
        def _round_to_int(val):
            return int(Decimal(str(val)).quantize(0, rounding=ROUND_HALF_UP))

        if charge_item.charge_type == 'fixed':
            # 根据单位决定计费方式：元/日、元/月、元/年
            if '日' in unit:
                # 按天计费，需要起止日期
                if billing_start_date and billing_end_date:
                    days = (billing_end_date - billing_start_date).days + 1
                    val = price * days
                    return _round_to_int(val)
                else:
                    # 没有日期则按 1 天计
                    val = price * 1
                    return _round_to_int(val)
            elif '年' in unit:
                # 按年计费：按年价格 * 年数（或按月换算）
                if billing_start_date and billing_end_date:
                    years = (billing_end_date.year - billing_start_date.year)
                    # 简化按整年计算
                    if years <= 0:
                        years = 1
                    val = price * years
                    return _round_to_int(val)
                else:
                    val = price * max(1, months // 12)
                    return _round_to_int(val)
            else:
                # 小时/度等扩展支持
                if '小时' in unit or '时' in unit:
                    # 按小时计费，需要起止时间（精确到小时）
                    if billing_start_date and billing_end_date:
                        seconds = (billing_end_date - billing_start_date).total_seconds()
                        hours = max(1, math.ceil(seconds / 3600.0))
                        val = price * hours
                        return _round_to_int(val)
                    else:
                        val = price * 1
                        return _round_to_int(val)
                if '度' in unit:
                    # 用于按用量计费（如电表度数）。
                    # 若传入 usage（用量），按用量计费；否则退回到按月计费的行为（或需要手动输入）。
                    if usage is not None:
                        val = price * float(usage)
                        return _round_to_int(val)
                    else:
                        val = price * months
                        return _round_to_int(val)
                # 默认按月
                val = price * months
                return _round_to_int(val)
        elif charge_item.charge_type == 'area':
            # 按面积计费，单位同样支持日/月/年
            if '日' in unit:
                if billing_start_date and billing_end_date:
                    days = (billing_end_date - billing_start_date).days + 1
                    val = price * resident_area * days
                    return _round_to_int(val)
                else:
                    val = price * resident_area * 1
                    return _round_to_int(val)
            elif '年' in unit:
                if billing_start_date and billing_end_date:
                    years = (billing_end_date.year - billing_start_date.year)
                    if years <= 0:
                        years = 1
                    val = price * resident_area * years
                    return _round_to_int(val)
                else:
                    val = price * resident_area * max(1, months // 12)
                    return _round_to_int(val)
            else:
                val = price * resident_area * months
                return _round_to_int(val)
        elif charge_item.charge_type == 'manual':
            # 手动：直接使用输入金额（四舍五入到整数元）
            return _round_to_int(manual_amount)
        else:
            return 0.0

