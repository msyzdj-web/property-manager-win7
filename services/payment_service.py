"""
缴费管理服务
"""
from datetime import datetime
import math
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from models.payment import Payment
from models.resident import Resident
from models.charge_item import ChargeItem
from models.database import SessionLocal
from decimal import Decimal, ROUND_HALF_UP
from utils.logger import logger


class PaymentService:
    """缴费管理服务类"""
    
    @staticmethod
    def get_all_payments(db: Session = None):
        """获取所有缴费记录"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            return db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).order_by(Payment.period.desc(), Payment.created_at.desc()).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_payment_by_id(payment_id: int, db: Session = None):
        """根据ID获取缴费记录"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            return db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(Payment.id == payment_id).first()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_payments_by_period(period: str, db: Session = None):
        """根据周期获取缴费记录"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            return db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(Payment.period == period).order_by(
                Payment.paid, Payment.created_at.desc()
            ).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_unpaid_payments_by_period(period: str, db: Session = None):
        """根据周期获取未缴费记录"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            return db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(
                and_(Payment.period == period, Payment.paid == 0)
            ).order_by(Payment.created_at.desc()).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_payments_by_resident(resident_id: int, db: Session = None):
        """根据住户获取缴费记录"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            return db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(Payment.resident_id == resident_id).order_by(
                Payment.period.desc(), Payment.created_at.desc()
            ).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def create_payment(resident_id: int, charge_item_id: int, period: str, 
                      billing_start_date, billing_end_date, billing_months: int,
                      amount: float, usage: float = None, db: Session = None):
        """创建缴费记录（生成账单）
        
        Args:
            resident_id: 住户ID
            charge_item_id: 收费项目ID
            period: 缴费周期（格式：YYYY-MM）
            billing_start_date: 计费开始日期
            billing_end_date: 计费结束日期
            billing_months: 计费周期数（月数）
            amount: 总金额
        """
        logger.log_operation("CREATE_PAYMENT_START",
                           f"resident_id={resident_id}, charge_item_id={charge_item_id}, period={period}, amount={amount}, usage={usage}")

        if db is None:
            db = SessionLocal()
        try:
            # 计算并规范化 billing_months，确保与开始/结束日期一致
            def calc_months(start_date, end_date):
                if not start_date or not end_date:
                    return billing_months if billing_months and billing_months > 0 else 1
                years = end_date.year - start_date.year
                months = years * 12 + (end_date.month - start_date.month)
                if end_date.day >= start_date.day:
                    months += 1
                return months if months > 0 else 1

            billing_months = calc_months(billing_start_date, billing_end_date)

            payment = Payment(
                resident_id=resident_id,
                charge_item_id=charge_item_id,
                period=period,
                billing_start_date=billing_start_date,
                billing_end_date=billing_end_date,
                billing_months=billing_months,
                paid_months=0,
                amount=amount,
                paid_amount=0,
                paid=0,
                usage=usage
            )
            db.add(payment)
            db.commit()
            db.refresh(payment)
            # 在关闭会话前加载关联对象，避免DetachedInstanceError
            _ = payment.resident
            _ = payment.charge_item
            logger.log_operation("CREATE_PAYMENT_SUCCESS", f"Created payment id={payment.id}")
            return payment
        except Exception as e:
            logger.log_error(e, f"CREATE_PAYMENT_FAILED: resident_id={resident_id}, charge_item_id={charge_item_id}")
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def update_payment(payment_id: int, resident_id: int = None, charge_item_id: int = None,
                       period: str = None, billing_start_date = None, billing_end_date = None,
                       billing_months: int = None, amount: float = None, usage: float = None, db: Session = None):
        """更新已有缴费记录"""
        logger.log_operation("UPDATE_PAYMENT_START", f"payment_id={payment_id}")
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("缴费记录不存在")

            if resident_id is not None:
                payment.resident_id = resident_id
            if charge_item_id is not None:
                payment.charge_item_id = charge_item_id
            if period is not None:
                payment.period = period
            if billing_start_date is not None:
                payment.billing_start_date = billing_start_date
            if billing_end_date is not None:
                payment.billing_end_date = billing_end_date
            # 重新计算 billing_months 如果未显式传入但有起止日期
            if billing_months is not None:
                payment.billing_months = billing_months
            else:
                try:
                    if billing_start_date and billing_end_date:
                        years = billing_end_date.year - billing_start_date.year
                        months = years * 12 + (billing_end_date.month - billing_start_date.month)
                        if billing_end_date.day >= billing_start_date.day:
                            months += 1
                        payment.billing_months = months if months > 0 else 1
                except Exception:
                    pass
            if amount is not None:
                payment.amount = amount
            if usage is not None:
                payment.usage = usage

            db.commit()
            db.refresh(payment)
            _ = payment.resident
            _ = payment.charge_item
            logger.log_operation("UPDATE_PAYMENT_SUCCESS", f"payment_id={payment_id}")
            return payment
        except Exception as e:
            logger.log_error(e, f"UPDATE_PAYMENT_FAILED: payment_id={payment_id}")
            db.rollback()
            raise e
        finally:
            if close_db and db is not None:
                db.close()
    
    @staticmethod
    def mark_paid(payment_id: int, paid_months: int = None, paid_units: float = None, operator: str = '', db: Session = None):
        """标记为已缴费（支持部分缴费）
        
        支持两种模式：
        - 按月缴费（兼容原逻辑）：传入 paid_months（int）
        - 按单位缴费（度/天/小时）：传入 paid_units（float），函数会根据 payment.charge_item.unit 将其转换为金额
        
        Args:
            payment_id: 缴费记录ID
            paid_months: 缴费周期数（月数），如果为None则缴清全部
            paid_units: 按收费单位的数量（如度/小时/天），优先于 paid_months
            operator: 操作员
        """
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            payment = db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("缴费记录不存在")
            
            # 如果传入 paid_units，则按收费单位计算本次缴费金额（degree/hour/day）
            paid_amount_this_time = 0
            if paid_units is not None:
                unit = (payment.charge_item.unit or '').lower() if payment.charge_item else ''
                price = float(payment.charge_item.price) if payment.charge_item and payment.charge_item.price is not None else 0.0
                # 小时：向上取整到小时
                if ('小时' in unit or '时' in unit):
                    units_to_pay = int(math.ceil(float(paid_units)))
                # 天：按天数向上取整
                elif ('天' in unit or '日' in unit):
                    units_to_pay = int(math.ceil(float(paid_units)))
                # 度：支持小数
                elif '度' in unit:
                    units_to_pay = float(paid_units)
                else:
                    # 回退到按月逻辑（将 paid_units 视作月数）
                    units_to_pay = int(math.ceil(float(paid_units)))

                # 计算金额并四舍五入到整数元
                try:
                    paid_amount_this_time = int(Decimal(str(price * float(units_to_pay))).quantize(0, rounding=ROUND_HALF_UP))
                except Exception:
                    paid_amount_this_time = int(round(price * float(units_to_pay)))
                # 更新已缴金额与已缴月数/标记（已缴单位信息通过 paid_amount/单价 反推显示）
                try:
                    prev_paid = Decimal(str(payment.paid_amount or 0))
                except Exception:
                    prev_paid = Decimal(str(float(payment.paid_amount or 0.0)))
                payment.paid_amount = float((prev_paid + Decimal(str(paid_amount_this_time))))
                # 如果已缴金额覆盖总金额，则标记已缴清
                try:
                    total_amt = float(payment.amount or 0.0)
                except Exception:
                    total_amt = 0.0
                if payment.paid_amount >= total_amt:
                    payment.paid = 1
            else:
                # 按月的旧逻辑：如果未指定缴费月数，则缴清全部
                if paid_months is None:
                    paid_months = payment.billing_months - payment.paid_months
                
                # 检查缴费月数是否超过剩余未缴费月数
                remaining_months = payment.billing_months - payment.paid_months
                if paid_months > remaining_months:
                    raise ValueError(f"缴费月数不能超过剩余未缴费月数（剩余{remaining_months}月）")
                
                if paid_months <= 0:
                    raise ValueError("缴费月数必须大于0")
                
                # 计算本次缴费金额（按比例计算）
                # 按月分摊并四舍五入到整数元（元）
                try:
                    monthly_amount_raw = Decimal(str(payment.amount)) / Decimal(str(payment.billing_months))
                except Exception:
                    monthly_amount_raw = Decimal(str(float(payment.amount) / payment.billing_months))
                monthly_amount = int(monthly_amount_raw.quantize(0, rounding=ROUND_HALF_UP))
                paid_amount_this_time = int((monthly_amount_raw * Decimal(str(paid_months))).quantize(0, rounding=ROUND_HALF_UP))
                
                # 更新缴费信息
                payment.paid_months += paid_months
                # 累加已交金额（保持为数值）
                try:
                    prev_paid = Decimal(str(payment.paid_amount or 0))
                except Exception:
                    prev_paid = Decimal(str(float(payment.paid_amount or 0.0)))
                payment.paid_amount = float((prev_paid + Decimal(str(paid_amount_this_time))))

            # 记录最近一次缴费时间（即便是部分缴费也记录时间）
            payment.paid_time = datetime.now()

            # 如果全部缴清，标记为已缴费
            if payment.paid_months >= payment.billing_months:
                payment.paid = 1
            
            payment.operator = operator

            # 创建流水记录（使用同一 db session）
            try:
                from services.payment_transaction_service import PaymentTransactionService
                PaymentTransactionService.create_transaction(payment_id=payment.id, amount=paid_amount_this_time, operator=operator, db=db)
            except Exception:
                # 流水失败不应该阻止主流程，记录但继续
                import traceback
                print("记录付款流水失败：", traceback.format_exc())

            db.commit()
            db.refresh(payment)
            # 确保关联对象已加载
            _ = payment.resident
            _ = payment.charge_item
            # 记录流水（使用同一 db session） - paid_amount_this_time 必须在此之前计算
            try:
                from services.payment_transaction_service import PaymentTransactionService
                if paid_amount_this_time and paid_amount_this_time > 0:
                    PaymentTransactionService.create_transaction(payment_id=payment.id, amount=paid_amount_this_time, operator=operator, db=db)
            except Exception:
                # 流水失败不应该阻止主流程，记录但继续
                import traceback
                print("记录付款流水失败：", traceback.format_exc())
            return payment
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def mark_unpaid(payment_id: int, db: Session = None):
        """标记为未缴费"""
        if db is None:
            db = SessionLocal()
        try:
            # 使用joinedload预加载关联对象，避免DetachedInstanceError
            payment = db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            ).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("缴费记录不存在")
            
            payment.paid = 0
            payment.paid_time = None
            payment.operator = None
            
            db.commit()
            db.refresh(payment)
            # 确保关联对象已加载
            _ = payment.resident
            _ = payment.charge_item
            return payment
        except Exception as e:
            db.rollback()
            raise e
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def delete_payment(payment_id: int, db: Session = None):
        """删除缴费记录"""
        logger.log_operation("DELETE_PAYMENT_START", f"payment_id={payment_id}")

        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                raise ValueError("缴费记录不存在")

            db.delete(payment)
            db.commit()
            logger.log_operation("DELETE_PAYMENT_SUCCESS", f"Deleted payment id={payment_id}")
            return True
        except Exception as e:
            logger.log_error(e, f"DELETE_PAYMENT_FAILED: payment_id={payment_id}")
            db.rollback()
            raise e
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def delete_payments_batch(payment_ids: list, db: Session = None):
        """批量删除缴费记录（使用单个数据库会话以提高性能和避免死锁）"""
        logger.log_operation("DELETE_PAYMENTS_BATCH_START", f"payment_ids={payment_ids}")

        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True

        try:
            deleted_count = 0
            failed_deletes = []

            for payment_id in payment_ids:
                try:
                    payment = db.query(Payment).filter(Payment.id == payment_id).first()
                    if payment:
                        db.delete(payment)
                        deleted_count += 1
                        logger.log_operation("DELETE_PAYMENT_BATCH_ITEM_SUCCESS", f"payment_id={payment_id}")
                    else:
                        failed_deletes.append((payment_id, "缴费记录不存在"))
                        logger.log_error(ValueError("缴费记录不存在"), f"DELETE_PAYMENT_BATCH_ITEM_NOT_FOUND: payment_id={payment_id}")
                except Exception as e:
                    failed_deletes.append((payment_id, str(e)))
                    logger.log_error(e, f"DELETE_PAYMENT_BATCH_ITEM_FAILED: payment_id={payment_id}")

            db.commit()
            logger.log_operation("DELETE_PAYMENTS_BATCH_SUCCESS", f"deleted={deleted_count}, failed={len(failed_deletes)}")
            return deleted_count, failed_deletes

        except Exception as e:
            logger.log_error(e, "DELETE_PAYMENTS_BATCH_FAILED")
            db.rollback()
            raise e
        finally:
            if close_db and db is not None:
                db.close()
    
    @staticmethod
    def search_payments(keyword: str, period: str = None, db: Session = None):
        """搜索缴费记录（按房号、姓名、收费项目）"""
        if db is None:
            db = SessionLocal()
        try:
            query = db.query(Payment).options(
                joinedload(Payment.resident),
                joinedload(Payment.charge_item)
            )
            
            # 如果指定了周期，先过滤周期
            if period:
                query = query.filter(Payment.period == period)
            
            # 搜索关键词
            # 支持输入格式： "building-unit-room" 或 "unit-room" 或普通关键字
            import re
            parts = re.findall(r'\d+', keyword)
            if len(parts) == 3:
                b, u, rno = parts
                query = query.join(Resident).join(ChargeItem).filter(
                    (Resident.building == str(b)) &
                    (Resident.unit == str(u)) &
                    (Resident.room_no.like(f"%{rno}%"))
                )
            elif len(parts) == 2:
                a, b = parts
                # treat as unit-room or building-room depending on data; try both
                query = query.join(Resident).join(ChargeItem).filter(
                    ((Resident.unit == str(a)) & (Resident.room_no.like(f"%{b}%"))) |
                    ((Resident.building == str(a)) & (Resident.room_no.like(f"%{b}%")))
                )
            else:
                keyword_like = f"%{keyword}%"
                query = query.join(Resident).join(ChargeItem).filter(
                    (Resident.room_no.like(keyword_like)) |
                    (Resident.name.like(keyword_like)) |
                    (Resident.phone.like(keyword_like)) |
                    (ChargeItem.name.like(keyword_like))
                )
            
            return query.order_by(Payment.period.desc(), Payment.created_at.desc()).all()
        finally:
            if db is not None:
                db.close()
    
    @staticmethod
    def get_statistics_by_period(period: str, db: Session = None):
        """获取周期统计信息"""
        if db is None:
            db = SessionLocal()
        try:
            total_count = db.query(Payment).filter(Payment.period == period).count()
            paid_count = db.query(Payment).filter(
                and_(Payment.period == period, Payment.paid == 1)
            ).count()
            unpaid_count = total_count - paid_count
            
            total_amount = db.query(func.sum(Payment.amount)).filter(
                Payment.period == period
            ).scalar()
            total_amount = float(total_amount) if total_amount else 0.0
            
            paid_amount = db.query(func.sum(Payment.amount)).filter(
                and_(Payment.period == period, Payment.paid == 1)
            ).scalar()
            paid_amount = float(paid_amount) if paid_amount else 0.0
            
            unpaid_amount = total_amount - paid_amount
            
            return {
                'total_count': total_count,
                'paid_count': paid_count,
                'unpaid_count': unpaid_count,
                'total_amount': total_amount,
                'paid_amount': paid_amount,
                'unpaid_amount': unpaid_amount
            }
        finally:
            if db is not None:
                db.close()

    @staticmethod
    def get_daily_sequence_for_payment(payment, db: Session = None):
        """返回指定 payment 在其创建日期的当天序号（从1开始），用于票据序号生成。
        逻辑：统计当日所有 created_at 在当日范围内且 id <= payment.id 的记录数。
        """
        from datetime import datetime, timedelta
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            created_at = getattr(payment, 'created_at', None)
            if not created_at:
                created_at = datetime.now()
            start = datetime(created_at.year, created_at.month, created_at.day)
            end = start + timedelta(days=1)
            count = db.query(func.count(Payment.id)).filter(
                Payment.created_at >= start,
                Payment.created_at < end,
                Payment.id <= payment.id
            ).scalar()
            return int(count) if count else 0
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def get_daily_sequence_for_date(date: datetime = None, db: Session = None):
        """返回指定日期（缺省为今天）的当日序号（下一个序号），用于票据序号生成。
        实现：统计该日已有的 payments 数量，并返回 count + 1。
        """
        from datetime import datetime, timedelta
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            if date is None:
                date = datetime.now()
            start = datetime(date.year, date.month, date.day)
            end = start + timedelta(days=1)
            count = db.query(func.count(Payment.id)).filter(
                Payment.created_at >= start,
                Payment.created_at < end
            ).scalar()
            return int(count) + 1
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def get_daily_sequence_for_date(target_date, db: Session = None):
        """返回指定日期的当日序号（从1开始），用于按打印日期生成票据序号。
        逻辑：统计当日所有 created_at 在当日范围内的记录数并返回 count+1。
        """
        from datetime import datetime, timedelta
        close_db = False
        if db is None:
            db = SessionLocal()
            close_db = True
        try:
            start = datetime(target_date.year, target_date.month, target_date.day)
            end = start + timedelta(days=1)
            count = db.query(func.count(Payment.id)).filter(
                Payment.created_at >= start,
                Payment.created_at < end
            ).scalar()
            cnt = int(count) if count else 0
            return cnt + 1
        finally:
            if close_db and db is not None:
                db.close()

    @staticmethod
    def get_statistics_by_year(year: int, db: Session = None):
        """按年获取统计信息（按收费项目分组）"""
        if db is None:
            db = SessionLocal()
        try:
            # 统计年度内的账单金额（使用 billing_start_date 年份或 period 字符串匹配）
            payments = db.query(Payment).join(ChargeItem).filter(
                func.strftime('%Y', Payment.billing_start_date) == f"{year:04d}"
            ).all()
            # 按年汇总：总账单金额、已缴金额、欠费金额；并按收费项目分别统计 total/paid/unpaid
            total_amount = 0.0
            total_paid = 0.0
            by_item = {}
            for p in payments:
                amt = float(p.amount) if p.amount else 0.0
                paid = float(p.paid_amount) if p.paid_amount else 0.0
                total_amount += amt
                total_paid += paid
                name = p.charge_item.name if p.charge_item else '未知'
                entry = by_item.get(name)
                if not entry:
                    entry = {'total': 0.0, 'paid': 0.0}
                    by_item[name] = entry
                entry['total'] += amt
                entry['paid'] += paid

            # 构造按项目列表，包含 total/paid/unpaid
            by_item_list = []
            for name, v in by_item.items():
                unpaid = v['total'] - v['paid']
                by_item_list.append((name, v['total'], v['paid'], unpaid))
            by_item_list.sort(key=lambda x: x[1], reverse=True)

            return {
                'year': year,
                'total_amount': total_amount,
                'paid_amount': total_paid,
                'unpaid_amount': total_amount - total_paid,
                'by_item': by_item_list
            }
        finally:
            if db is not None:
                db.close()

