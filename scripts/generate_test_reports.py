#!/usr/bin/env python3
"""
生成测试数据并导出日/月/年报表到 exports/ 以便人工验证排版和统计逻辑。

用法：
    python scripts/generate_test_reports.py
会在项目的 exports/ 目录生成：
 - test_daily_YYYY-MM.xlsx
 - test_monthly_YYYY-MM.xlsx
 - test_year_YYYY.xlsx
"""
import os
from datetime import datetime, timedelta, date

from models.database import init_db, SessionLocal
from services.resident_service import ResidentService
from services.charge_service import ChargeService
from services.payment_service import PaymentService
from utils.report_generator import ReportGenerator


def ensure_exports_dir():
    exports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'exports')
    os.makedirs(exports_dir, exist_ok=True)
    return exports_dir


def create_sample_data():
    init_db()
    db = SessionLocal()
    try:
        # 创建或获取住户
        r = ResidentService.create_resident('1-TEST-001', '测试住户A', phone='13800000000', area=60.0, move_in_date=date(2020, 1, 1))
        # 创建收费项目：日费、月费、年费
        daily = ChargeService.create_charge_item('临时停车费(日)', 10.0, 'fixed', unit='元/日')
        monthly = ChargeService.create_charge_item('物业费(月)', 200.0, 'fixed', unit='元/月')
        yearly = ChargeService.create_charge_item('年服务费(年)', 1200.0, 'fixed', unit='元/年')

        # 生成示例缴费记录
        # 日费：2025-12-20 至 2025-12-25（6天）
        start_day = datetime(2025, 12, 20)
        end_day = datetime(2025, 12, 25)
        PaymentService.create_payment(
            resident_id=r.id,
            charge_item_id=daily.id,
            period='2025-12',
            billing_start_date=start_day,
            billing_end_date=end_day,
            billing_months=0,
            amount=ChargeService.calculate_amount(daily, billing_start_date=start_day, billing_end_date=end_day)
        )

        # 月费：2025-11-01 至 2025-11-30（1月）
        start_m = datetime(2025, 11, 1)
        end_m = datetime(2025, 11, 30)
        PaymentService.create_payment(
            resident_id=r.id,
            charge_item_id=monthly.id,
            period='2025-11',
            billing_start_date=start_m,
            billing_end_date=end_m,
            billing_months=1,
            amount=ChargeService.calculate_amount(monthly, resident_area=60.0, months=1)
        )

        # 年费：2025-01-01 至 2025-12-31（1年）
        start_y = datetime(2025, 1, 1)
        end_y = datetime(2025, 12, 31)
        PaymentService.create_payment(
            resident_id=r.id,
            charge_item_id=yearly.id,
            period='2025',
            billing_start_date=start_y,
            billing_end_date=end_y,
            billing_months=12,
            amount=ChargeService.calculate_amount(yearly, billing_start_date=start_y, billing_end_date=end_y)
        )

        return True
    except Exception as e:
        print("创建测试数据出错：", e)
        return False
    finally:
        db.close()


def generate_reports():
    exports = ensure_exports_dir()
    # 日报（按月）
    period = '2025-12'
    daily_path = os.path.join(exports, f"test_daily_{period}.xlsx")
    ReportGenerator.generate_daily_report(period, daily_path)
    print("已生成日度报表：", daily_path)

    # 月报
    period2 = '2025-11'
    monthly_path = os.path.join(exports, f"test_monthly_{period2}.xlsx")
    ReportGenerator.generate_monthly_report(period2, monthly_path)
    print("已生成月度报表：", monthly_path)

    # 年报
    year = '2025'
    yearly_path = os.path.join(exports, f"test_year_{year}.xlsx")
    ReportGenerator.generate_year_report(year, yearly_path)
    print("已生成年度报表：", yearly_path)


if __name__ == '__main__':
    ok = create_sample_data()
    if ok:
        generate_reports()
    else:
        print("未能创建测试数据，停止生成报表。")


