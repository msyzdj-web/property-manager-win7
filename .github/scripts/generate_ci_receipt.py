#!/usr/bin/env python3
from datetime import datetime
import os

def main():
    try:
        # Minimal fake objects to avoid DB dependency
        class FakeResident:
            def __init__(self):
                self.name = "测试户"
                self.room_no = "1-1-101"
                self.full_room_no = self.room_no

        class FakeCharge:
            def __init__(self):
                self.id = 1
                self.name = "物业费"

        class FakePayment:
            def __init__(self):
                self.id = 1
                self.resident = FakeResident()
                self.charge_item = FakeCharge()
                self.charge_item_id = 1
                self.amount = 1616.00
                self.paid_amount = 1616.00
                self.billing_start_date = datetime(2025,11,16)
                self.billing_end_date = datetime(2026,11,15)
                self.billing_months = 12
                self.paid_months = 12
                self.created_at = datetime.now()

        os.makedirs('exports', exist_ok=True)
        # Import ReceiptPrinter from project
        from utils.printer import ReceiptPrinter
        rp = ReceiptPrinter(paper_size='收据纸 (241×93mm)', top_offset_mm=3.0,
                            company_font_scale_adj=0.95, content_font_scale=1.0)
        p = FakePayment()
        # Try the PIL renderer (no GUI) to produce an image and write diag
        try:
            rp._render_receipt_to_image_pil(p, 'exports/receipt_ci_000001.png', dpi=180, payment_date_str=None, payment_seq=1)
        except Exception as e:
            print("PIL render failed:", e)
        try:
            rp._write_runtime_diag(p, payment_id=p.id, image_size={'w':241,'h':93})
        except Exception as e:
            print("Writing diag failed:", e)
        print("CI sample receipt generation finished")
    except Exception as exc:
        print("CI sample receipt generation fatal error:", exc)
        raise

if __name__ == "__main__":
    main()


