"""
打印工具模块
"""
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPainter, QFont, QFontMetrics, QPen, QImage, QColor, QPixmap
import tempfile
import os
from PyQt5.QtCore import Qt, QRect
from datetime import datetime, timedelta
import sys

from services.payment_service import PaymentService
from decimal import Decimal, ROUND_HALF_UP


class ReceiptPrinter:
    """收据打印类"""
    
    # 仅保留目标收据纸尺寸 (毫米)
    PAPER_SIZES = {
        '收据纸 (241×93mm)': (241, 93),
    }
    
    def __init__(self, paper_size='收据纸 (241×93mm)', top_offset_mm: float = 0.0, company_font_scale_adj: float = 1.0, content_font_scale: float = 1.0, safe_margin_mm: float = 8.0, safe_margin_left_mm: float = None, safe_margin_right_mm: float = None):
        """
        top_offset_mm: 页面内容向上平移的毫米数（用于针式打印机微调）
        company_font_scale_adj: 公司标题与主标题的字体缩放系数（<1 缩小, >1 放大）
        """
        # 强制只支持目标收据纸尺寸
        self.paper_size = '收据纸 (241×93mm)'
        # 调整项
        self.top_offset_mm = float(top_offset_mm)
        self.company_font_scale_adj = float(company_font_scale_adj)
        # 正文字号缩放系数（影响表格与正文字体大小）
        self.content_font_scale = float(content_font_scale)
        # 安全边距（毫米），用于针式打印时确保内容不被切掉
        self.safe_margin_mm = float(safe_margin_mm)
        # 在 render/print 时会计算为像素值并赋给此属性
        self._top_offset_px = 0
        # 可选左右安全边距（mm），若未提供则使用 safe_margin_mm
        self.safe_margin_left_mm = float(safe_margin_left_mm) if safe_margin_left_mm is not None else None
        self.safe_margin_right_mm = float(safe_margin_right_mm) if safe_margin_right_mm is not None else None
        # 确保在创建 QPrinter 前存在 QApplication，避免 headless 调用时崩溃（render/print 调用会在 GUI 环境下已有 QApplication）
        self._created_qapp = False
        try:
            if QApplication.instance() is None:
                _app = QApplication([])  # 临时创建 Qt 应用以支持 QPrinter/QPainter
                self._created_qapp = True
        except Exception:
            # 如果创建失败则继续，后续渲染可能仍失败但不应阻塞初始化
            self._created_qapp = False
        self.printer = QPrinter(QPrinter.HighResolution)
        
        # 仅支持收据纸 (241×93mm)
        # NOTE:
        # 不在此处强制设置 QPrinter 的自定义纸张尺寸，因为在 macOS 上
        # 在显示打印对话框之前改变打印机的纸张可能触发系统错误提示：
        # "Changing the destination paper to Custom would cause a conflict that cannot be resolved."
        # 因此我们只在需要输出为 PDF 时再为 QPrinter 设置页面尺寸，避免在物理打印前修改打印机状态。
        if paper_size in self.PAPER_SIZES:
            w_mm, h_mm = self.PAPER_SIZES[paper_size]
        else:
            # 若传入非预定义值，强制使用收据纸尺寸
            w_mm, h_mm = self.PAPER_SIZES['收据纸 (241×93mm)']
        # 保存目标物理尺寸供渲染/导出使用；不要在此处调用 self.printer.setPageSizeMM(...)
        self._target_w_mm = float(w_mm)
        self._target_h_mm = float(h_mm)
        
        # 根据纸张方向设置
        # 所有纸张尺寸均已定义了准确的 W, H。对于自定义尺寸，使用 Portrait 模式通常能最准确地对应 (W, H)。
        self.printer.setOrientation(QPrinter.Portrait)
    
    def print_receipt(self, payment_id, output_file: str = None):
        """打印收据"""
        try:
            payment = PaymentService.get_payment_by_id(payment_id)
            if not payment:
                return False
            # 如果指定了 output_file，则直接输出为 PDF，跳过打印对话框
            if output_file:
                # 如果是 PDF 输出，我们先渲染到一张高分辨率 PNG，再把该图像绘制到 QPrinter 以生成 PDF（兼容性更好）
                if output_file.lower().endswith('.pdf'):
                    # 先创建打印流水以获取当日序号，再渲染到临时 PNG
                    try:
                        from services.print_service import PrintService
                        print_log = PrintService.create_print_log(payment_id=payment.id)
                        payment_date_str = payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d')
                        payment_seq = print_log.seq
                    except Exception:
                        payment_date_str = payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d')
                        payment_seq = None
                    # 先渲染到临时 PNG，传入序号以在图片中显示
                    tmp_dir = tempfile.gettempdir()
                    tmp_png = os.path.join(tmp_dir, f"receipt_tmp_{payment_id}.png")
                    ok_img = self.render_receipt_to_image(payment_id, tmp_png, dpi=300, payment_date_str=payment_date_str, payment_seq=payment_seq)
                    if not ok_img:
                        return False
                    # 设置打印机输出到 PDF 文件
                    try:
                        self.printer.setOutputFormat(QPrinter.PdfFormat)
                        # 再次强制设置页面尺寸与分辨率，防止 PDF 模式下重置为 A4
                        try:
                            from PyQt5.QtCore import QSizeF
                            if self.paper_size in self.PAPER_SIZES:
                                w_mm, h_mm = self.PAPER_SIZES[self.paper_size]
                                self.printer.setPageSizeMM(QSizeF(w_mm, h_mm))
                        except Exception:
                            pass
                        try:
                            # 强制设置为 300 DPI，用于生成与渲染图片一致的像素尺寸
                            self.printer.setResolution(300)
                        except Exception:
                            pass
                        self.printer.setOrientation(QPrinter.Portrait)
                    except Exception:
                        pass
                    self.printer.setOutputFileName(output_file)
                    # 将图片绘制到打印机页面
                    painter = QPainter()
                    # PDF 输出路径：优先使用打印机报告的分辨率（通常已被设置为 300）
                    try:
                        self._render_dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else 300
                    except Exception:
                        self._render_dpi = 300
                    if not painter.begin(self.printer):
                        # 清理临时文件
                        try:
                            if os.path.exists(tmp_png):
                                os.remove(tmp_png)
                        except:
                            pass
                        return False
                    try:
                        image = QImage(tmp_png)
                        
                        # 获取页面绘制区域
                        page_rect = self.printer.pageRect()
                        rect = QRect(int(page_rect.x()), int(page_rect.y()), int(page_rect.width()), int(page_rect.height()))
                        
                        # 保持图片比例绘制，防止被强制拉伸
                        # 计算保持比例的目标尺寸
                        from PyQt5.QtCore import QSize
                        target_size = image.size().scaled(rect.size(), Qt.KeepAspectRatio)
                        
                        # 居中显示
                        x = rect.left() + (rect.width() - target_size.width()) // 2
                        y = rect.top() + (rect.height() - target_size.height()) // 2
                        target_rect = QRect(x, y, target_size.width(), target_size.height())
                        
                        painter.drawImage(target_rect, image)
                    finally:
                        painter.end()
                        # 清理临时文件
                        try:
                            if os.path.exists(tmp_png):
                                os.remove(tmp_png)
                        except:
                            pass
                    return True
                else:
                    # 其他输出类型（例如直接打印到文件）仍按原先方式设置输出文件名
                    try:
                        self.printer.setOutputFormat(QPrinter.PdfFormat)
                    except Exception:
                        pass
                    self.printer.setOutputFileName(output_file)
            else:
                # 在展示打印对话框前尝试启用 FullPage 并清空页面边距以避免打印机驱动强制缩放或左右不对称
                try:
                    # 尝试强制页面尺寸与分辨率（避免驱动在物理打印时进行额外缩放）
                    try:
                        from PyQt5.QtCore import QSizeF
                        if sys.platform != 'darwin':
                            if self.paper_size in self.PAPER_SIZES:
                                w_mm, h_mm = self.PAPER_SIZES[self.paper_size]
                                try:
                                    self.printer.setPageSizeMM(QSizeF(w_mm, h_mm))
                                except Exception:
                                    pass
                            try:
                                self.printer.setResolution(300)
                            except Exception:
                                pass
                            try:
                                self.printer.setFullPage(True)
                            except Exception:
                                pass
                            try:
                                self.printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
                            except Exception:
                                pass
                        else:
                            # macOS：仍然启用 FullPage 与 0 页边距尝试，但不强制 setPageSizeMM（避免 Custom 冲突提示）
                            try:
                                self.printer.setFullPage(True)
                            except Exception:
                                pass
                            try:
                                self.printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
                            except Exception:
                                pass
                    except Exception:
                        # 任何设置失败不阻塞打印流程
                        pass
                except Exception:
                    # 外层设置失败也不阻塞打印流程
                    pass
                # 显示打印对话框（不在此处修改纸张尺寸以避免 macOS 的 Custom 纸张冲突提示）
                print_dialog = QPrintDialog(self.printer)
                if print_dialog.exec_() != QPrintDialog.Accepted:
                    return False

                # 开始打印：如果之前未为 PDF 创建流水，则现在创建（适用于直接打印）
                try:
                    if 'payment_seq' not in locals() or payment_seq is None:
                        from services.print_service import PrintService
                        print_log = PrintService.create_print_log(payment_id=payment.id)
                        payment_date_str = payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d')
                        payment_seq = print_log.seq
                except Exception:
                    payment_date_str = payment_date_str if 'payment_date_str' in locals() else (payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d'))
                    payment_seq = payment_seq if 'payment_seq' in locals() else None

                # 渲染一张与物理打印机分辨率相匹配的图片，然后按目标物理宽度（mm）缩放绘制到打印机页面上。
                # 这样可以避免直接修改打印机的纸张尺寸，同时保证图像在物理上的实际宽度为目标宽度（例如 241mm）。
                try:
                    dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else 300
                except Exception:
                    dpi = 300

                # 先渲染到临时 PNG（使用打印机 DPI，以便像素与物理尺寸一一对应）
                tmp_dir = tempfile.gettempdir()
                tmp_png = os.path.join(tmp_dir, f"receipt_tmp_{payment_id}.png")
                # 计算打印机可用宽度（像素）并传入渲染函数，以便生成与打印机可绘制区域匹配的图像
                try:
                    page_rect = self.printer.pageRect()
                    mm_per_inch = 25.4
                    try:
                        left_safe_px = int((self.safe_margin_left_mm if self.safe_margin_left_mm is not None else self.safe_margin_mm) / mm_per_inch * dpi)
                    except Exception:
                        left_safe_px = int(self.safe_margin_mm / mm_per_inch * dpi)
                    try:
                        right_safe_px = int((self.safe_margin_right_mm if self.safe_margin_right_mm is not None else self.safe_margin_mm) / mm_per_inch * dpi)
                    except Exception:
                        right_safe_px = int(self.safe_margin_mm / mm_per_inch * dpi)
                    # 给打印驱动留点缓冲，但不要过大（2% 或至少 10px，限制最大 40px）
                    driver_pad = int(min(max(int(page_rect.width() * 0.02), 10), 40))
                    max_available_width = max(0, int(page_rect.width()) - left_safe_px - right_safe_px - driver_pad)
                    # 在 Windows 环境下对可用宽度做小幅收缩，避免某些驱动对接收到的图像做二次放大/适配导致打印变宽
                    try:
                        if sys.platform.startswith('win') and max_available_width:
                            max_available_width = int(max_available_width * 0.98)
                    except Exception:
                        pass
                except Exception:
                    max_available_width = None

                ok_img = self.render_receipt_to_image(payment_id, tmp_png, dpi=dpi, payment_date_str=payment_date_str, payment_seq=payment_seq, max_width_px=max_available_width)
                if not ok_img or not os.path.exists(tmp_png):
                    # 回退：尝试直接使用向量绘制（旧行为）
                    try:
                        # 计算并设置顶部偏移与安全边距（像素），以便 _draw_receipt 使用
                        mm_per_inch = 25.4
                        self._top_offset_px = int(self.top_offset_mm / mm_per_inch * dpi)
                        left_mm = self.safe_margin_left_mm if self.safe_margin_left_mm is not None else self.safe_margin_mm
                        right_mm = self.safe_margin_right_mm if self.safe_margin_right_mm is not None else self.safe_margin_mm
                        self._safe_margin_left_px = int(left_mm / mm_per_inch * dpi) if left_mm is not None else 0
                        self._safe_margin_right_px = int(right_mm / mm_per_inch * dpi) if right_mm is not None else 0
                    except Exception:
                        self._top_offset_px = 0
                        self._safe_margin_left_px = 0
                        self._safe_margin_right_px = 0
                    painter = QPainter()
                    try:
                        self._render_dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else dpi
                    except Exception:
                        try:
                            self._render_dpi = int(dpi)
                        except Exception:
                            self._render_dpi = 300
                    painter.begin(self.printer)
                    page_rect = self.printer.pageRect()
                    self._draw_receipt(painter, page_rect, payment, payment_date_str=payment_date_str, payment_seq=payment_seq)
                    painter.end()
                    return True

                # 使用图片绘制到打印机页面（按目标物理宽度缩放并水平居中）
                painter = QPainter()
                try:
                    self._render_dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else dpi
                except Exception:
                    try:
                        self._render_dpi = int(dpi)
                    except Exception:
                        self._render_dpi = 300
                if not painter.begin(self.printer):
                    try:
                        if os.path.exists(tmp_png):
                            os.remove(tmp_png)
                    except Exception:
                        pass
                    return False
                try:
                    image = QImage(tmp_png)
                    # 记录诊断信息，帮助定位 Win 打包后驱动差异问题（导出到 exports 目录）
                    try:
                        diag = {}
                        diag['dpi'] = dpi
                        try:
                            pr = self.printer.pageRect()
                            diag['page_rect'] = {'x': int(pr.x()), 'y': int(pr.y()), 'w': int(pr.width()), 'h': int(pr.height())}
                            # 记录我们用于实际绘制的矩形大小（便于诊断）
                            try:
                                # 使用实际渲染的图片大小与打印机 pageRect 取交集作为有效绘制区域
                                effective_w = min(image.width(), int(pr.width()))
                                effective_h = min(image.height(), int(pr.height()))
                                diag['effective_draw_rect'] = {'x': int(pr.x()), 'y': int(pr.y()), 'w': int(effective_w), 'h': int(effective_h)}
                            except Exception:
                                diag['effective_draw_rect'] = None
                        except Exception:
                            diag['page_rect'] = None
                        diag['image_size'] = {'w': image.width(), 'h': image.height()}
                        diag['target_mm'] = {'w_mm': self._target_w_mm, 'h_mm': self._target_h_mm}
                        exports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'exports'))
                        try:
                            os.makedirs(exports_dir, exist_ok=True)
                        except Exception:
                            pass
                        diag_path = os.path.join(exports_dir, f'print_diag_{payment_id}.json')
                        try:
                            import json
                            with open(diag_path, 'w', encoding='utf-8') as f:
                                json.dump(diag, f, ensure_ascii=False, indent=2)
                        except Exception:
                            pass
                    except Exception:
                        pass
                    # 计算期望的像素宽高（以打印机 DPI 为基准）
                    mm_per_inch = 25.4
                    desired_w_px = int(self._target_w_mm / mm_per_inch * dpi)
                    desired_h_px = int(self._target_h_mm / mm_per_inch * dpi)

                    # 缩放图片以匹配目标物理宽度（保留纵横比），但限制不要超过打印机可绘制区域（考虑驱动不可打印边距）
                    from PyQt5.QtCore import QSize
                    page_rect = self.printer.pageRect()

                    # 计算基于用户设置的安全边距（像素）
                    try:
                        left_safe_px = int((self.safe_margin_left_mm if self.safe_margin_left_mm is not None else self.safe_margin_mm) / mm_per_inch * dpi)
                    except Exception:
                        left_safe_px = int(self.safe_margin_mm / mm_per_inch * dpi)
                    try:
                        right_safe_px = int((self.safe_margin_right_mm if self.safe_margin_right_mm is not None else self.safe_margin_mm) / mm_per_inch * dpi)
                    except Exception:
                        right_safe_px = int(self.safe_margin_mm / mm_per_inch * dpi)

                    # 给打印驱动留点缓冲，但不要过大（2% 或至少 10px，限制最大 40px）
                    driver_pad = int(min(max(int(page_rect.width() * 0.02), 10), 40))

                    # 计算页面上可用的最大图像宽度（像素）
                    max_available_width = max(0, page_rect.width() - left_safe_px - right_safe_px - driver_pad)

                    # 期望的目标像素（基于物理目标宽度）
                    desired_w_px = int(self._target_w_mm / mm_per_inch * dpi)
                    desired_h_px = int(self._target_h_mm / mm_per_inch * dpi)

                    # 限制目标宽度不要超出可用宽度
                    use_w_px = min(desired_w_px, max_available_width) if max_available_width > 0 else min(desired_w_px, page_rect.width() - driver_pad)

                    target_size = image.size().scaled(QSize(use_w_px, desired_h_px), Qt.KeepAspectRatio)

                    # 计算水平位置：以页面居中为首选，仅在越界时应用安全边距与驱动缓冲
                    centered_x = int(page_rect.x() + (page_rect.width() - target_size.width()) // 2)
                    # 允许的最小/最大 x（基于安全边距和驱动缓冲）
                    min_allowed_x = int(page_rect.x() + left_safe_px)
                    max_allowed_x = int(page_rect.x() + page_rect.width() - target_size.width() - right_safe_px - driver_pad)
                    # 如果计算出来的 max < min，则尝试放宽 driver_pad，再退回到页左边界作为兜底
                    if max_allowed_x < min_allowed_x:
                        relaxed_pad = max(0, driver_pad - 10)
                        max_allowed_x = int(page_rect.x() + page_rect.width() - target_size.width() - right_safe_px - relaxed_pad)
                        if max_allowed_x < min_allowed_x:
                            min_allowed_x = int(page_rect.x())
                            max_allowed_x = int(page_rect.x() + page_rect.width() - target_size.width())
                    # 以居中为首选，然后裁剪到允许范围内
                    x = centered_x
                    if x < min_allowed_x:
                        x = min_allowed_x
                    if x > max_allowed_x:
                        x = max_allowed_x

                    # 将 top offset 作为向上微调（在 render 时已应用，但在物理页上仍允许少量偏移）
                    try:
                        top_px = int(self._top_offset_px)
                    except Exception:
                        top_px = 0
                    y = int(page_rect.y() + max(0, top_px))

                    # 最终保证不会越界（确保右侧保留 right_safe_px）
                    if x + target_size.width() + right_safe_px + driver_pad > page_rect.x() + page_rect.width():
                        x = max(int(page_rect.x()), page_rect.x() + page_rect.width() - int(target_size.width()) - right_safe_px - driver_pad)

                    target_rect = QRect(x, y, int(target_size.width()), int(target_size.height()))
                    painter.drawImage(target_rect, image)
                finally:
                    painter.end()
                    try:
                        if os.path.exists(tmp_png):
                            os.remove(tmp_png)
                    except Exception:
                        pass
                return True

        except Exception as e:
            print(f"打印失败: {str(e)}")
            return False

    def _num_to_rmb_upper(self, num):
        """将数字金额转换为中文大写（人民币）简易实现，适用于0.00～999999999.99"""
        units = ["元", "拾", "佰", "仟", "万", "拾", "佰", "仟", "亿"]
        nums = ["零", "壹", "贰", "叁", "肆", "伍", "陆", "柒", "捌", "玖"]
        if num is None:
            return ""
        try:
            n = round(float(num) + 0.0000001, 2)
        except:
            return ""
        integer = int(n)
        fraction = int(round((n - integer) * 100))
        if integer == 0:
            int_part = "零元"
        else:
            int_part = ""
            s = str(integer)[::-1]
            for i, ch in enumerate(s):
                digit = int(ch)
                unit = units[i] if i < len(units) else ""
                if digit != 0:
                    int_part = nums[digit] + unit + int_part
                else:
                    # 避免连续零
                    if not int_part.startswith("零"):
                        int_part = "零" + int_part
            int_part = int_part.rstrip("零")
            if not int_part.endswith("元"):
                int_part = int_part + "元"
        # 小数部分
        jiao = fraction // 10
        fen = fraction % 10
        frac_part = ""
        if jiao == 0 and fen == 0:
            frac_part = "整"
        else:
            if jiao > 0:
                frac_part += nums[jiao] + "角"
            if fen > 0:
                frac_part += nums[fen] + "分"
        return int_part + frac_part

    def _draw_receipt(self, painter: QPainter, page_rect: QRect, payment, payment_date_str: str = None, payment_seq: int = None):
        """在给定 painter 和页面矩形上绘制收据（不负责 begin/end）"""
        try:
            width = page_rect.width()
            height = page_rect.height()
            
            # 项目目标：仅支持 241×93mm（宽纸），将所有绘制逻辑视为宽纸模式
            is_narrow_paper = False
            is_wide_paper = True
            is_small_paper = True
            
            # 布局策略：全部基于宽度的百分比计算 PixelSize，确保在任何 DPI 下字体相对纸张宽度的大小一致
            # A4 纸宽较宽，正文字体占比可以小一些；小票纸窄，字体占比要大一些才能看清
            if is_narrow_paper:
                base_font_scale = 0.035  # 小票纸窄(80mm): 字体需较大
                margin_scale = 0.02
                line_spacing_scale = 0.04
            elif is_wide_paper:
                # 针式打印纸(241x93mm): 宽而扁，高度受限，但为了可读性适度增大字号与行高
                base_font_scale = 0.016  # 从 1.3% 提升到 1.6% 宽度以放大字体
                margin_scale = 0.02
                line_spacing_scale = 0.025
            else:
                # A4
                base_font_scale = 0.018  # 1.8% width
                margin_scale = 0.05
                line_spacing_scale = 0.025

            # 计算基准像素大小
            base_pixel_size = int(width * base_font_scale)
            # 应用用户可调的内容字号缩放（影响表格与正文字体）
            try:
                base_pixel_size = int(base_pixel_size * (self.content_font_scale if hasattr(self, 'content_font_scale') else 1.0))
            except Exception:
                pass
            
            # 字体生成辅助函数
            def get_font(size_factor, bold=False):
                # 使用 setPixelSize 确保精确控制像素高度
                f = QFont('SimSun')
                f.setPixelSize(int(base_pixel_size * size_factor))
                if bold:
                    f.setBold(True)
                return f

            # 字体定义（公司标题与主标题可通过 self.company_font_scale_adj 缩放）
            comp_scale = (self.company_font_scale_adj if hasattr(self, 'company_font_scale_adj') else 1.0)
            company_font = get_font(1.8 * comp_scale, True)   # 标题大字
            title_font = get_font(1.6 * comp_scale, True)     # 收据字样
            normal_font = get_font(1.0)          # 正文
            small_font = get_font(0.9)           # 小字
            bold_font = get_font(1.0, True)      # 正文粗体

            # 页面尺寸与边距（支持左右独立安全边距）
            base_margin = int(width * margin_scale)
            # 最小页边距，避免内容过贴边导致打印被裁切（针式打印机更保守）
            if base_margin < 30:
                base_margin = 30
            try:
                left_safe_px = int(getattr(self, '_safe_margin_left_px', 0))
            except Exception:
                left_safe_px = 0
            try:
                right_safe_px = int(getattr(self, '_safe_margin_right_px', 0))
            except Exception:
                right_safe_px = 0
            margin_left = max(base_margin, left_safe_px)
            margin_right = max(base_margin, right_safe_px)
            content_width = width - margin_left - margin_right
            # 全局缩小表格宽度 10mm（转换为当前渲染 DPI 的像素）
            try:
                mm_per_inch = 25.4
                dpi_for_render = int(getattr(self, '_render_dpi', 300))
                reduce_px = int(10 / mm_per_inch * dpi_for_render)
                if reduce_px > 0:
                    content_width = max(0, content_width - reduce_px)
            except Exception:
                pass
            # 应用顶部像素偏移（render/print 路径会提前将 self.top_offset_mm 转换为 self._top_offset_px）
            try:
                top_offset_px = int(getattr(self, '_top_offset_px', 0))
                y = max(0, base_margin - top_offset_px)
            except Exception:
                y = base_margin
            
            # 行高计算
            if is_wide_paper:
                # 241x93 高度受限，但为了保证安全距离与可读性，适度提高行高
                row_height = int(base_pixel_size * 1.9)
            else:
                row_height = int(base_pixel_size * 2.2)  # 行高为字号的 2.2 倍
            
            # 顶部公司名称（居中、加下划线效果用线）
            # 尝试绘制LOGO
            try:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.jpg')
                if os.path.exists(logo_path):
                    logo_pixmap = QPixmap(logo_path)
                    if not logo_pixmap.isNull():
                        # LOGO高度设为行高的2.5倍
                        logo_h = int(row_height * 2.5)
                        scaled_logo = logo_pixmap.scaledToHeight(logo_h, Qt.SmoothTransformation)
                        # 绘制在左边距位置
                        painter.drawPixmap(margin_left, y, scaled_logo)
            except Exception:
                pass

            painter.setFont(company_font)
            company_rect = QRect(margin_left, y, content_width, int(row_height * 1.5))
            painter.drawText(company_rect, Qt.AlignCenter, "四川盛涵物业服务有限公司")
            y += company_rect.height()
            # 保持公司抬头与标题之间合理间距，避免过度压缩导致下方签名区域被挤出页底
            y += int(row_height * 0.10) if is_wide_paper else int(row_height * 0.25)

            # 收据大标题
            painter.setFont(title_font)
            title_rect = QRect(margin_left, y, content_width, int(row_height * 1.5))
            painter.drawText(title_rect, Qt.AlignCenter, "收费收据")
            # 标题与表格之间的间距，保留一定空间以保证整体布局不拥挤
            y += title_rect.height() + int(row_height * 0.35)
            
            # 收据编号
            painter.setFont(normal_font)
            # 表格宽度: 小票 100% content, A4 85% content
            if is_small_paper:
                table_width = content_width
            else:
                table_width = int(content_width * 0.9)
            
            start_x = margin_left + int((content_width - table_width) / 2)
            
            # 票据编号：前缀为缴费记录创建日期（YYYYMMDD），后三位为打印流水序号（若外部提供则使用，否则预览时读取当日下一个序号）
            try:
                if payment_date_str is None:
                    payment_date_str = payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d')
                if payment_seq is None:
                    from services.print_service import PrintService
                    payment_seq = PrintService.get_today_sequence()
            except Exception:
                payment_date_str = payment_date_str or (payment.created_at.strftime('%Y%m%d') if getattr(payment, 'created_at', None) else datetime.now().strftime('%Y%m%d'))
                payment_seq = payment_seq or (getattr(payment, 'id', 1) % 1000 if getattr(payment, 'id', None) else 1)
            receipt_no = f"NO:{payment_date_str}{int(payment_seq):03d}"
            painter.drawText(QRect(start_x, y - row_height, table_width, row_height), Qt.AlignRight | Qt.AlignBottom, receipt_no)

            # 定义列宽
            if is_narrow_paper:
                # 小票纸(80mm)：大幅压缩时间列，给项目和金额留空间
                c1 = int(table_width * 0.25)
                c2 = int(table_width * 0.35)
                c3 = int(table_width * 0.22)
                c4 = table_width - c1 - c2 - c3
            else:
                # A4 和 针式宽纸(241mm)：宽度充足，使用标准比例
                c1 = int(table_width * 0.25)
                c2 = int(table_width * 0.40)
                c3 = int(table_width * 0.18)
                c4 = table_width - c1 - c2 - c3
            col_widths = [c1, c2, c3, c4]


            # 户名、房号、日期一行（对齐到表格列）
            info_y = y
            now = datetime.now()
            # 日期格式（包含时分秒）
            # 生成房号显示，优先使用 Resident 的 building/unit/room_no 组合（确保使用 '-' 分隔）
            def format_full_room(resident):
                try:
                    b = getattr(resident, 'building', '') or ''
                    u = getattr(resident, 'unit', '') or ''
                    r = getattr(resident, 'room_no', '') or ''
                    parts = []
                    if b != '':
                        parts.append(str(b).strip())
                    if u != '':
                        parts.append(str(u).strip())
                    if r != '':
                        # 如果 room_no 本身包含 spaces like '11 101', normalize by removing spaces
                        rn = str(r).strip().replace(' ', '-')
                        parts.append(rn)
                    if parts:
                        return "-".join(parts)
                except Exception:
                    pass
                # fallback to existing attributes
                try:
                    return getattr(resident, 'full_room_no', getattr(resident, 'room_no', ''))
                except Exception:
                    return ''

            room_display_val = format_full_room(payment.resident)
            if is_narrow_paper:
                date_text = now.strftime("%Y.%m.%d %H:%M:%S")
                info_text = f"户名:{payment.resident.name} 房号:{room_display_val}"
            else:
                date_text = f"日期：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"
                info_text = f"户名：{payment.resident.name}    房号：{room_display_val}"
            
            painter.drawText(QRect(start_x, info_y, c1 + c2, row_height), Qt.AlignLeft | Qt.AlignVCenter, info_text)
            painter.drawText(QRect(start_x + c1 + c2, info_y, c3 + c4, row_height), Qt.AlignRight | Qt.AlignVCenter, date_text)
            y += row_height + (0 if is_wide_paper else int(row_height * 0.2))

            # 表格区域设置
            table_top = y
            # 计算明细行：仅显示实际存在的非空项目，避免打印空行
            details = []
            try:
                item_name = payment.charge_item.name if payment.charge_item else ""
                billing_period = ""
                if payment.billing_start_date and payment.billing_end_date:
                    # 显示时将结束日期显示为实际结束日前一天（用户要求）
                    try:
                        end_display = (payment.billing_end_date - timedelta(days=1))
                    except Exception:
                        end_display = payment.billing_end_date
                    if is_small_paper:
                        billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}-{end_display.strftime('%Y.%m.%d')}"
                    else:
                        billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}–{end_display.strftime('%Y.%m.%d')}"
                    if payment.billing_start_date and payment.billing_end_date:
                        try:
                            end_display = (payment.billing_end_date - timedelta(days=1))
                        except Exception:
                            end_display = payment.billing_end_date
                        if is_small_paper:
                            billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}-{end_display.strftime('%Y.%m.%d')}"
                        else:
                            billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}–{end_display.strftime('%Y.%m.%d')}"
                # 将金额四舍五入为整数元用于显示
                try:
                    amt_int = int(Decimal(str(payment.amount)).quantize(0, rounding=ROUND_HALF_UP)) if getattr(payment, 'amount', None) is not None else 0
                    amount_text = f"{amt_int:.2f}" if getattr(payment, 'amount', None) is not None else ""
                except Exception:
                    try:
                        amt_int = int(round(float(payment.amount))) if getattr(payment, 'amount', None) is not None else 0
                        amount_text = f"{amt_int:.2f}" if getattr(payment, 'amount', None) is not None else ""
                    except Exception:
                        amount_text = str(payment.amount) if getattr(payment, 'amount', None) is not None else ""
                if (item_name and item_name.strip()) or (billing_period and billing_period.strip()) or (amount_text and amount_text.strip()):
                    details.append((item_name, billing_period, amount_text))
            except Exception:
                # 如果读取字段失败，保持 details 为空以避免占位行
                details = []

            # 如果没有明细行，但存在金额，则插入默认一行（保留原有打印样式）
            try:
                if not details and (getattr(payment, 'amount', None) is not None):
                    default_name = ""
                    try:
                        default_name = payment.charge_item.name if payment.charge_item and getattr(payment.charge_item, 'name', None) else "物业费"
                    except Exception:
                        default_name = "物业费"
                    try:
                        amt_int = int(Decimal(str(payment.amount)).quantize(0, rounding=ROUND_HALF_UP))
                        amount_text_def = f"{amt_int:.2f}"
                    except Exception:
                        try:
                            amt_int = int(round(float(payment.amount)))
                            amount_text_def = f"{amt_int:.2f}"
                        except Exception:
                            amount_text_def = str(payment.amount)
                    # billing_period 如果有则使用之前计算的值，否则尝试重建
                    if not billing_period:
                        try:
                            if payment.billing_start_date and payment.billing_end_date:
                                end_display = (payment.billing_end_date - timedelta(days=1))
                                billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}–{end_display.strftime('%Y.%m.%d')}"
                        except Exception:
                            billing_period = ""
                    details.append((default_name, billing_period, amount_text_def))
            except Exception:
                pass

            # 限制最大显示行数以适配纸张类型（避免过长）
            if is_narrow_paper:
                max_rows = 4
            elif is_wide_paper:
                max_rows = 3
            else:
                max_rows = 8

            num_rows = min(max_rows, len(details)) if details else 0

            # 如果没有明细行但存在金额，补一行默认明细以保证“物业费”等关键行不丢失
            if num_rows == 0:
                try:
                    # 尝试构造默认明细行：优先使用 charge_item.name，否则使用“物业费”
                    default_name = payment.charge_item.name if getattr(payment, 'charge_item', None) and getattr(payment.charge_item, 'name', None) else "物业费"
                except Exception:
                    default_name = "物业费"
                try:
                    amt_int = int(Decimal(str(payment.amount)).quantize(0, rounding=ROUND_HALF_UP)) if getattr(payment, 'amount', None) is not None else 0
                    amount_text_def = f"{amt_int:.2f}"
                except Exception:
                    try:
                        amt_int = int(round(float(getattr(payment, 'amount', 0))))
                        amount_text_def = f"{amt_int:.2f}"
                    except Exception:
                        amount_text_def = str(getattr(payment, 'amount', ""))
                # 试着重建 billing_period
                try:
                    if payment.billing_start_date and payment.billing_end_date:
                        end_display = (payment.billing_end_date - timedelta(days=1))
                        billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')}–{end_display.strftime('%Y.%m.%d')}"
                except Exception:
                    billing_period = ""
                details = [(default_name, billing_period, amount_text_def)]
                num_rows = 1
            note_rows = 1
            total_table_rows = 1 + num_rows + 1 + note_rows
            table_height = total_table_rows * row_height

            # 若表格过高以致签名/底部空间不足，则减少明细行数以保证签名能正常绘制
            try:
                sig_est_height = int(row_height * 2.5)  # 预留签名与提示行高度
                # 使用左右较大的边距作为底部安全边距参考
                available_space = height - max(margin_left, margin_right) - table_top - sig_est_height
                max_total_rows = max(1, available_space // max(1, row_height))
                if total_table_rows > max_total_rows:
                    # 需减少 num_rows
                    min_fixed_rows = 1 + 1 + note_rows  # header + total + note rows
                    new_num_rows = max(0, int(max_total_rows - min_fixed_rows))
                    num_rows = min(num_rows, new_num_rows)
                    total_table_rows = 1 + num_rows + 1 + note_rows
                    table_height = total_table_rows * row_height
            except Exception:
                pass

            # 绘制外框与网格
            pen = QPen(Qt.black)
            pen.setWidth(max(1, int(width * 0.001))) # 细线
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawRect(start_x, table_top, table_width, table_height)
            for i in range(total_table_rows + 1):
                y_line = int(table_top + i * row_height)
                painter.drawLine(start_x, y_line, start_x + table_width, y_line)
            
            # 竖线
            x_acc = start_x
            painter.drawLine(x_acc, table_top, x_acc, table_top + table_height)
            for w in col_widths:
                x_acc += w
                painter.drawLine(x_acc, table_top, x_acc, table_top + table_height)
            
            # 恢复默认笔
            default_pen = QPen(Qt.black)
            default_pen.setWidth(0)
            painter.setPen(default_pen)

            # 表头
            painter.setFont(bold_font)
            headers = ["收费项目", "起止时间", "金额(元)", "备注"]
            x = start_x
            h_padding = int(row_height * 0.2)
            for idx, header in enumerate(headers):
                w = col_widths[idx]
                painter.drawText(QRect(x + 2, y, w - 4, row_height), Qt.AlignCenter, header)
                x += w
            y += row_height

            # 明细行：按实际存在的 details 绘制，避免空行
            painter.setFont(normal_font)
            for idx in range(num_rows):
                item_name, billing_period, amount_text = details[idx]
                x = start_x
                painter.drawText(QRect(x + 2, y, col_widths[0] - 4, row_height), Qt.AlignLeft | Qt.AlignVCenter, item_name)
                x += col_widths[0]
                if is_small_paper:
                    painter.setFont(small_font)
                painter.drawText(QRect(x + 1, y, col_widths[1] - 2, row_height), Qt.AlignCenter, billing_period)
                if is_small_paper:
                    painter.setFont(normal_font)
                x += col_widths[1]
                painter.drawText(QRect(x + 1, y, col_widths[2] - 2, row_height), Qt.AlignCenter, amount_text)
                y += row_height

            # 如果有实付信息
            if getattr(payment, 'paid_months', 0) and payment.paid_months > 0 and payment.billing_start_date:
                try:
                    def add_months(dt, months):
                        month = dt.month - 1 + months
                        year = dt.year + month // 12
                        month = month % 12 + 1
                        import calendar
                        day = min(dt.day, calendar.monthrange(year, month)[1])
                        return dt.replace(year=year, month=month, day=day)
                    start = payment.billing_start_date
                    end_paid = add_months(start, int(payment.paid_months))
                    # 实收周期通常表示到实际结束日前一日，调整为包含前一日
                    try:
                        from datetime import timedelta
                        end_paid = end_paid - timedelta(days=1)
                    except Exception:
                        pass
                    if is_small_paper:
                        paid_period_text = f"{start.strftime('%Y.%m.%d')}-{end_paid.strftime('%Y.%m.%d')}"
                    else:
                        paid_period_text = f"{start.strftime('%Y.%m.%d')}–{end_paid.strftime('%Y.%m.%d')}"
                    try:
                        paid_amt_int = int(Decimal(str(payment.paid_amount)).quantize(0, rounding=ROUND_HALF_UP)) if payment.paid_amount else 0
                        paid_amount_text = f"{paid_amt_int:.2f}" if payment.paid_amount else "0.00"
                    except Exception:
                        try:
                            paid_amt_int = int(round(float(payment.paid_amount))) if payment.paid_amount else 0
                            paid_amount_text = f"{paid_amt_int:.2f}" if payment.paid_amount else "0.00"
                        except Exception:
                            paid_amount_text = str(payment.paid_amount or "0")
                    
                    # 第一行：实收周期
                    note_y = y
                    painter.fillRect(start_x + 1, note_y + 1, table_width - 2, row_height - 2, QColor('white'))
                    painter.drawText(QRect(start_x + 5, note_y, table_width - 10, row_height), Qt.AlignLeft | Qt.AlignVCenter, f"实收周期: {paid_period_text}")
                    y += row_height
                    # 第二行：实收金额
                    note_y = y
                    painter.fillRect(start_x + 1, note_y + 1, table_width - 2, row_height - 2, QColor('white'))
                    painter.drawText(QRect(start_x + 5, note_y, table_width - 10, row_height), Qt.AlignLeft | Qt.AlignVCenter, f"实收金额: {paid_amount_text}")
                    y += row_height
                except Exception as _:
                    # 回退 y
                    y = table_top + (1 + num_rows) * row_height
                    pass
            else:
                 y = table_top + (1 + num_rows) * row_height

            # 合计行
            total_y = y
            painter.setFont(bold_font)
            painter.drawText(QRect(start_x + 2, total_y, col_widths[0] - 4, row_height), Qt.AlignLeft | Qt.AlignVCenter, "合计大写")
            
            try:
                total_amount = float(payment.amount) if payment.amount else 0.0
            except:
                total_amount = 0.0
            try:
                paid_amount = float(payment.paid_amount) if getattr(payment, 'paid_amount', None) else 0.0
            except:
                paid_amount = 0.0
            display_amount = paid_amount if paid_amount > 0 else total_amount
            upper_amount = self._num_to_rmb_upper(display_amount)
            painter.drawText(QRect(start_x + c1, total_y, c2, row_height), Qt.AlignCenter | Qt.AlignVCenter, upper_amount)
            painter.setFont(bold_font)
            painter.drawText(QRect(start_x + c1 + c2, total_y, c3, row_height), Qt.AlignLeft | Qt.AlignVCenter, "合计小写")
            painter.setFont(normal_font)
            # 合计显示为整数元
            try:
                disp_int = int(Decimal(str(display_amount)).quantize(0, rounding=ROUND_HALF_UP))
                display_amount_str = f"{disp_int:.2f}"
            except Exception:
                try:
                    disp_int = int(round(float(display_amount)))
                    display_amount_str = f"{disp_int:.2f}"
                except Exception:
                    display_amount_str = f"{float(display_amount):.2f}"
            painter.drawText(QRect(start_x + c1 + c2 + c3, total_y, c4, row_height), Qt.AlignCenter | Qt.AlignVCenter, f"{display_amount_str}元")
            y += row_height

            # 提示行
            note_y = y
            painter.fillRect(start_x + 1, note_y + 1, table_width - 2, row_height - 2, QColor('white'))
            painter.drawText(QRect(start_x + 5, note_y, table_width - 10, row_height), Qt.AlignLeft | Qt.AlignVCenter, "请确认您的缴费金额，如有疑问请咨询物业服务中心")
            y += row_height + (0 if is_wide_paper else int(row_height * 0.5))

            # 底部签名
            sig_height = row_height
            # 改为紧跟内容下方，宽纸模式下尽量紧凑
            sig_offset = 0 if is_wide_paper else int(row_height * 0.3)
            sig_y = y + sig_offset
            # 如果过低可能会超出页底，做保险检查并向上调整（保留少量额外间距）
            try:
                extra_pad = int(row_height * 0.5)
                bottom_limit = height - max(margin_left, margin_right) - sig_height - extra_pad
                if sig_y > bottom_limit:
                    sig_y = max(y, bottom_limit)
            except Exception:
                pass
            
            left_x = start_x
            right_x = start_x + int(table_width / 2)
            painter.drawText(QRect(left_x, sig_y, int(table_width/2), sig_height), Qt.AlignLeft | Qt.AlignVCenter, "收款人:")
            painter.drawText(QRect(right_x, sig_y, int(table_width/2), sig_height), Qt.AlignLeft | Qt.AlignVCenter, "收款单位盖章:")
        except Exception as e:
            # 在绘制层捕获异常以便调用者（打印或图像保存）能收到失败信号
            print(f"_draw_receipt 失败: {e}")
            raise


    def render_receipt_to_image(self, payment_id, output_path, dpi=300, payment_date_str: str = None, payment_seq: int = None, max_width_px: int = None, max_height_px: int = None):
        """将收据渲染为高分辨率 PNG 图像并保存"""
        try:
            payment = PaymentService.get_payment_by_id(payment_id)
            if not payment:
                return False
            
            # 只使用目标收据纸尺寸（241×93mm）
            w_mm, h_mm = self._target_w_mm, self._target_h_mm

            # 转换为像素（默认根据 dpi 计算），但允许调用方传入 max_width_px/max_height_px 以匹配打印机可绘制区域
            mm_per_inch = 25.4
            width_px = int(w_mm / mm_per_inch * dpi)
            height_px = int(h_mm / mm_per_inch * dpi)
            # 如果调用方提供了 max_width_px（例如打印时基于 printer.pageRect 计算的可用像素宽度），优先使用它并按纸张纵横比计算高度（除非同时提供 max_height_px）
            if max_width_px is not None:
                try:
                    width_px = int(max_width_px)
                    if max_height_px is not None:
                        height_px = int(max_height_px)
                    else:
                        # 保持纸张纵横比
                        height_px = int(width_px * (h_mm / w_mm))
                except Exception:
                    pass
            
            image = QImage(width_px, height_px, QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter()
            # 在渲染为图像时，按指定 dpi 将 top_offset_mm 转为像素用于 _draw_receipt
            try:
                self._top_offset_px = int(self.top_offset_mm / mm_per_inch * dpi)
            except Exception:
                self._top_offset_px = 0
            # 确保已存在 QApplication（QPrinter/QPainter 需要 Qt 应用环境）
            created_app = False
            try:
                if QApplication.instance() is None:
                    _app = QApplication([])
                    created_app = True
            except Exception:
                created_app = False
            painter.begin(image)
            
            # 使用与打印器相同的 page_rect（像素坐标）
            page_rect = QRect(0, 0, width_px, height_px)
            try:
                self._draw_receipt(painter, page_rect, payment, payment_date_str=payment_date_str, payment_seq=payment_seq)
                painter.end()
                # 保存图像（PNG）
                ok = image.save(output_path)
                # 如果我们临时创建了 QApplication，则退出它以释放资源（不影响主程序若已存在）
                try:
                    if created_app:
                        try:
                            _app.quit()
                        except Exception:
                            pass
                except Exception:
                    pass
                return ok
            except Exception as e:
                # Qt 渲染失败，尝试使用 PIL 回退生成可视化样张
                try:
                    try:
                        painter.end()
                    except Exception:
                        pass
                    return self._render_receipt_to_image_pil(payment, output_path, dpi=dpi, payment_date_str=payment_date_str, payment_seq=payment_seq)
                except Exception as e2:
                    print(f"render_receipt_to_image Qt 渲染失败: {e}, 回退 PIL 也失败: {e2}")
                    return False
        except Exception as e:
            print(f"render_receipt_to_image 失败: {e}")
            return False

    def _render_receipt_to_image_pil(self, payment, output_path, dpi=300, payment_date_str: str = None, payment_seq: int = None):
        """回退：使用 Pillow 生成简单的收据预览（在无法使用 Qt 绘制时使用）"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            # 简易布局：以像素为单位，按 dpi 计算尺寸
            mm_per_inch = 25.4
            # 仅支持收据纸 (241×93mm)
            if self.paper_size in self.PAPER_SIZES:
                w_mm, h_mm = self.PAPER_SIZES[self.paper_size]
            else:
                w_mm, h_mm = self.PAPER_SIZES['收据纸 (241×93mm)']
            width_px = int(w_mm / mm_per_inch * dpi)
            height_px = int(h_mm / mm_per_inch * dpi)
            img = Image.new('RGB', (width_px, height_px), 'white')
            draw = ImageDraw.Draw(img)

            # 字体尝试加载常见字体，否则使用默认
            try:
                font_big = ImageFont.truetype('SimSun.ttf', max(18, int(width_px * 0.03)))
                font_title = ImageFont.truetype('SimSun.ttf', max(16, int(width_px * 0.025)))
                font_norm = ImageFont.truetype('SimSun.ttf', max(12, int(width_px * 0.015)))
            except Exception:
                try:
                    font_big = ImageFont.truetype('Arial.ttf', max(18, int(width_px * 0.03)))
                    font_title = ImageFont.truetype('Arial.ttf', max(16, int(width_px * 0.025)))
                    font_norm = ImageFont.truetype('Arial.ttf', max(12, int(width_px * 0.015)))
                except Exception:
                    font_big = ImageFont.load_default()
                    font_title = ImageFont.load_default()
                    font_norm = ImageFont.load_default()

            # 文本内容准备（与 Qt 绘制保持一致的格式化）
            try:
                room_display = getattr(payment.resident, 'full_room_no', getattr(payment.resident, 'room_no', ''))
            except Exception:
                room_display = ''
            try:
                now = datetime.now()
            except Exception:
                now = None
            try:
                end_display = (payment.billing_end_date - timedelta(days=1)) if getattr(payment, 'billing_end_date', None) else None
            except Exception:
                end_display = getattr(payment, 'billing_end_date', None)
            if getattr(payment, 'billing_start_date', None) and end_display:
                billing_period = f"{payment.billing_start_date.strftime('%Y.%m.%d')} - {end_display.strftime('%Y.%m.%d')}"
            else:
                billing_period = ''
            receipt_no = f"NO:{(payment.created_at.strftime('%Y%m%d') if getattr(payment,'created_at',None) else (now.strftime('%Y%m%d') if now else ''))}{int(payment_seq or 1):03d}"

            # 绘制 header / title
            w_center = width_px // 2
            draw.text((w_center, int(height_px * 0.03)), "四川盛涵物业服务有限公司", fill='black', font=font_big, anchor='ms')
            draw.text((w_center, int(height_px * 0.08)), "收费收据", fill='black', font=font_title, anchor='ms')
            # 右上：票据号与日期
            if now:
                draw.text((width_px - 20, int(height_px * 0.03)), now.strftime('%Y年%m月%d日 %H:%M:%S'), fill='black', font=font_norm, anchor='rs')
            draw.text((width_px - 20, int(height_px * 0.07)), receipt_no, fill='black', font=font_norm, anchor='rs')

            # 基本信息
            draw.text((40, int(height_px * 0.15)), f"户名: {getattr(payment.resident,'name', '')}    房号: {room_display}", fill='black', font=font_norm)
            draw.text((40, int(height_px * 0.20)), f"实收周期: {billing_period}", fill='black', font=font_norm)
            draw.text((40, int(height_px * 0.25)), f"实收金额: {getattr(payment, 'paid_amount', getattr(payment, 'amount', ''))}", fill='black', font=font_norm)

            # 底部签名位置
            draw.text((40, int(height_px * 0.85)), "收款人:", fill='black', font=font_norm)
            draw.text((width_px // 2 + 40, int(height_px * 0.85)), "收款单位盖章:", fill='black', font=font_norm)

            img.save(output_path)
            return True
        except Exception as e:
            print(f"_render_receipt_to_image_pil 失败: {e}")
            return False

    def print_merged_receipt(self, payment_ids, output_file: str = None):
        """合并打印多笔账单到一张收据（payment_ids 为列表）"""
        try:
            if not payment_ids:
                return False
            payments = []
            for pid in payment_ids:
                p = PaymentService.get_payment_by_id(pid)
                if p:
                    payments.append(p)
            if not payments:
                return False

            # 如果指定了 output_file 则先渲染为 PNG，再输出到 PDF（与单据相同策略）
            if output_file and output_file.lower().endswith('.pdf'):
                tmp_dir = tempfile.gettempdir()
                tmp_png = os.path.join(tmp_dir, f"receipt_merged_tmp.png")
                ok_img = self.render_merged_receipt_to_image(payments, tmp_png, dpi=300)
                if not ok_img:
                    return False
                try:
                    self.printer.setOutputFormat(QPrinter.PdfFormat)
                    # 强制重新设置页面尺寸，防止 PDF 模式下重置为 A4
                    if self.paper_size in self.PAPER_SIZES:
                        w_mm, h_mm = self.PAPER_SIZES[self.paper_size]
                        from PyQt5.QtCore import QSizeF
                        self.printer.setPageSizeMM(QSizeF(w_mm, h_mm))
                    self.printer.setOrientation(QPrinter.Portrait)
                except Exception:
                    pass
                self.printer.setOutputFileName(output_file)
                painter = QPainter()
                try:
                    self._render_dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else 300
                except Exception:
                    self._render_dpi = 300
                if not painter.begin(self.printer):
                    try:
                        if os.path.exists(tmp_png):
                            os.remove(tmp_png)
                    except:
                        pass
                    return False
                try:
                    image = QImage(tmp_png)
                    page_rect = self.printer.pageRect()
                    rect = QRect(int(page_rect.x()), int(page_rect.y()), int(page_rect.width()), int(page_rect.height()))
                    
                    # 保持图片比例绘制
                    from PyQt5.QtCore import QSize
                    target_size = image.size().scaled(rect.size(), Qt.KeepAspectRatio)
                    
                    # 居中显示
                    x = rect.left() + (rect.width() - target_size.width()) // 2
                    y = rect.top() + (rect.height() - target_size.height()) // 2
                    target_rect = QRect(x, y, target_size.width(), target_size.height())
                    
                    painter.drawImage(target_rect, image)
                finally:
                    painter.end()
                    try:
                        if os.path.exists(tmp_png):
                            os.remove(tmp_png)
                    except:
                        pass
                return True

            # 否则显示打印对话框并打印
            print_dialog = QPrintDialog(self.printer)
            if print_dialog.exec_() != QPrintDialog.Accepted:
                return False

            # 计算并设置顶部偏移与安全边距（像素），以便 _draw_merged_receipt 使用
            try:
                dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else 300
            except Exception:
                dpi = 300
            try:
                mm_per_inch = 25.4
                self._top_offset_px = int(self.top_offset_mm / mm_per_inch * dpi)
                self._safe_margin_px = int(self.safe_margin_mm / mm_per_inch * dpi)
            except Exception:
                self._top_offset_px = 0
                self._safe_margin_px = 0

            painter = QPainter()
            try:
                self._render_dpi = int(self.printer.resolution()) if hasattr(self.printer, 'resolution') else dpi
            except Exception:
                try:
                    self._render_dpi = int(dpi)
                except Exception:
                    self._render_dpi = 300
            painter.begin(self.printer)
            page_rect = self.printer.pageRect()
            self._draw_merged_receipt(painter, page_rect, payments)
            painter.end()
            return True
        except Exception as e:
            print(f"print_merged_receipt 失败: {e}")
            return False

    def _draw_merged_receipt(self, painter: QPainter, page_rect: QRect, payments: list):
        """在单页内绘制多笔账单的合并收据（多行明细）"""
        try:
            width = page_rect.width()
            height = page_rect.height()

            # 布局参数计算（复用 _draw_receipt 的逻辑）
            # 判断纸张类型
            is_narrow_paper = width < height * 0.5
            is_wide_paper = width > height * 2
            is_small_paper = is_narrow_paper or is_wide_paper
            
            # 布局策略：基于宽度计算 PixelSize
            # 布局策略：基于宽度计算 PixelSize
            if is_wide_paper:
                # 宽纸适度放大基准字号并增加行高因子以提高可读性与安全边距
                base_font_scale = 0.016
                margin_scale = 0.02
                table_width_pct = 0.98
                row_height_factor = 1.9
            elif is_narrow_paper:
                base_font_scale = 0.035
                margin_scale = 0.02
                table_width_pct = 0.98
                row_height_factor = 2.2
            else:
                base_font_scale = 0.018
                margin_scale = 0.05
                table_width_pct = 0.90
                row_height_factor = 2.2

            base_pixel_size = int(width * base_font_scale)
            # 应用用户可调的内容字号缩放（影响表格与正文字体）
            try:
                base_pixel_size = int(base_pixel_size * (self.content_font_scale if hasattr(self, 'content_font_scale') else 1.0))
            except Exception:
                pass
            def get_font(size_factor, bold=False):
                f = QFont('SimSun')
                f.setPixelSize(int(base_pixel_size * size_factor))
                if bold: f.setBold(True)
                return f

            company_font = get_font(1.8, True)
            title_font = get_font(1.6, True)
            normal_font = get_font(1.0)
            small_font = get_font(0.9)
            bold_font = get_font(1.0, True)
            
            row_height = int(base_pixel_size * row_height_factor)

            # 边距（支持左右独立安全边距）
            base_margin = int(width * margin_scale)
            if base_margin < 30:
                base_margin = 30
            try:
                left_safe_px = int(getattr(self, '_safe_margin_left_px', 0))
            except Exception:
                left_safe_px = 0
            try:
                right_safe_px = int(getattr(self, '_safe_margin_right_px', 0))
            except Exception:
                right_safe_px = 0
            margin_left = max(base_margin, left_safe_px)
            margin_right = max(base_margin, right_safe_px)
            content_width = width - margin_left - margin_right
            # 全局缩小表格宽度 10mm（转换为当前渲染 DPI 的像素）
            try:
                mm_per_inch = 25.4
                dpi_for_render = int(getattr(self, '_render_dpi', 300))
                reduce_px = int(10 / mm_per_inch * dpi_for_render)
                if reduce_px > 0:
                    content_width = max(0, content_width - reduce_px)
            except Exception:
                pass
            try:
                top_offset_px = int(getattr(self, '_top_offset_px', 0))
                y = max(0, base_margin - top_offset_px)
            except Exception:
                y = base_margin

            # 绘制LOGO
            try:
                logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logo.jpg')
                if os.path.exists(logo_path):
                    logo_pixmap = QPixmap(logo_path)
                    if not logo_pixmap.isNull():
                        # LOGO高度设为行高的2.5倍
                        logo_h = int(row_height * 2.5)
                        scaled_logo = logo_pixmap.scaledToHeight(logo_h, Qt.SmoothTransformation)
                        painter.drawPixmap(margin_left, y, scaled_logo)
            except Exception:
                pass

            # 标题区域
            painter.setFont(company_font)
            title_rect = QRect(margin_left, y, content_width, int(row_height * 1.5))
            painter.drawText(title_rect, Qt.AlignCenter, "四川盛涵物业服务有限公司")
            # 宽纸且空间紧凑时，减少间距
            y += title_rect.height()
            if not is_wide_paper:
                 y += int(row_height * 0.1)
            
            painter.setFont(title_font)
            title_rect = QRect(margin_left, y, content_width, int(row_height * 1.5))
            painter.drawText(title_rect, Qt.AlignCenter, "收费收据（合并）")
            y += title_rect.height()
            if not is_wide_paper:
                y += int(row_height * 0.3)

            # 表格
            table_width = int(content_width * table_width_pct)
            start_x = margin_left + int((content_width - table_width) / 2)
            
            # 列宽分配
            if is_small_paper:
                col_widths = [int(table_width * 0.22), int(table_width * 0.38), int(table_width * 0.22), int(table_width * 0.18)]
            else:
                col_widths = [int(table_width * 0.25), int(table_width * 0.40), int(table_width * 0.18), int(table_width * 0.17)]
            
            if is_wide_paper:
                num_rows = max(1, len(payments))
            elif is_narrow_paper:
                num_rows = max(4, len(payments))
            else:
                num_rows = max(8, len(payments))
            total_table_rows = 1 + num_rows + 1 + 1
            table_height = total_table_rows * row_height

            pen = QPen(Qt.black)
            pen.setWidth(max(1, int(width * 0.001)))
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawRect(start_x, y, table_width, table_height)
            for i in range(total_table_rows + 1):
                y_line = int(y + i * row_height)
                painter.drawLine(start_x, y_line, start_x + table_width, y_line)

            x_acc = int(start_x)
            painter.drawLine(x_acc, int(y), x_acc, int(y + table_height))
            for w in col_widths:
                x_acc += int(w)
                painter.drawLine(x_acc, int(y), x_acc, int(y + table_height))
            
            default_pen = QPen(Qt.black)
            default_pen.setWidth(0)
            painter.setPen(default_pen)

            # 表头
            painter.setFont(bold_font)
            headers = ["收费项目", "起止时间", "金额（元）", "备注"]
            x = start_x
            for idx, header in enumerate(headers):
                w = col_widths[idx]
                painter.drawText(QRect(int(x + 6), int(y + 4), int(w - 12), int(row_height - 8)), Qt.AlignLeft | Qt.AlignVCenter, header)
                x += w
            y += row_height
            
            painter.setFont(normal_font)
            total_amount = 0.0
            total_paid_amount = 0.0
            for idx, p in enumerate(payments):
                if idx >= num_rows:
                    break
                item_name = p.charge_item.name if p.charge_item else ""
                # 如果存在已缴月数或已缴金额，优先显示实付周期与实付金额；否则显示账单周期与总额
                billing_period_line = ""
                try:
                    def add_months(dt, months):
                        month = dt.month - 1 + months
                        year = dt.year + month // 12
                        month = month % 12 + 1
                        import calendar
                        day = min(dt.day, calendar.monthrange(year, month)[1])
                        return dt.replace(year=year, month=month, day=day)

                    if getattr(p, 'paid_months', 0) and p.paid_months > 0 and p.billing_start_date:
                        start_paid = p.billing_start_date
                        end_paid = add_months(start_paid, int(p.paid_months))
                        try:
                            from datetime import timedelta
                            end_paid = end_paid - timedelta(days=1)
                        except Exception:
                            pass
                        billing_period_line = f"{start_paid.strftime('%Y.%m.%d')}–{end_paid.strftime('%Y.%m.%d')}"
                    else:
                        billing_period_line = f"{p.billing_start_date.strftime('%Y.%m.%d')}–{p.billing_end_date.strftime('%Y.%m.%d')}" if p.billing_start_date and p.billing_end_date else (p.period or "")
                except Exception:
                    billing_period_line = f"{p.period or ''}"

                try:
                    display_line_amount = float(p.paid_amount) if getattr(p, 'paid_amount', None) and float(p.paid_amount) > 0 else float(p.amount or 0.0)
                except Exception:
                    display_line_amount = float(p.amount or 0.0)

                # 显示为整数后保留两位小数
                try:
                    amt_int = int(Decimal(str(display_line_amount)).quantize(0, rounding=ROUND_HALF_UP))
                    amount_text = f"{amt_int:.2f}"
                except Exception:
                    try:
                        amt_int = int(round(float(display_line_amount)))
                        amount_text = f"{amt_int:.2f}"
                    except Exception:
                        amount_text = str(display_line_amount)
                painter.drawText(QRect(int(start_x + 6), int(y + 4), int(col_widths[0] - 12), int(row_height - 8)), Qt.AlignLeft | Qt.AlignVCenter, item_name)
                painter.drawText(QRect(int(start_x + col_widths[0] + 6), int(y + 4), int(col_widths[1] - 12), int(row_height - 8)), Qt.AlignCenter | Qt.AlignVCenter, billing_period_line)
                painter.drawText(QRect(int(start_x + col_widths[0] + col_widths[1] + 6), int(y + 4), int(col_widths[2] - 12), int(row_height - 8)), Qt.AlignCenter | Qt.AlignVCenter, amount_text)
                y += row_height
                total_amount += float(p.amount or 0.0)
                total_paid_amount += float(p.paid_amount or 0.0)

            # 合计行显示：优先显示已缴合计，否则显示账单合计
            display_amount = total_paid_amount if total_paid_amount > 0 else total_amount
            painter.setFont(bold_font)
            total_y = y
            painter.drawText(QRect(int(start_x + 6), int(total_y + 4), int(col_widths[0] - 12), int(row_height - 8)), Qt.AlignLeft | Qt.AlignVCenter, "合计金额大写")
            upper_amount = self._num_to_rmb_upper(display_amount)
            painter.setFont(normal_font)
            painter.drawText(QRect(int(start_x + col_widths[0] + 6), int(total_y + 4), int(col_widths[1] - 12), int(row_height - 8)), Qt.AlignCenter | Qt.AlignVCenter, upper_amount)
            painter.setFont(bold_font)
            painter.drawText(QRect(int(start_x + col_widths[0] + col_widths[1] + 6), int(total_y + 4), int(col_widths[2] - 12), int(row_height - 8)), Qt.AlignLeft | Qt.AlignVCenter, "合计金额小写")
            painter.setFont(normal_font)
            try:
                disp_int = int(Decimal(str(display_amount)).quantize(0, rounding=ROUND_HALF_UP))
                disp_text = f"{disp_int:.2f}元"
            except Exception:
                try:
                    disp_int = int(round(float(display_amount)))
                    disp_text = f"{disp_int:.2f}元"
                except Exception:
                    disp_text = f"{float(display_amount):.2f}元"
            painter.drawText(QRect(int(start_x + col_widths[0] + col_widths[1] + col_widths[2] + 6), int(total_y + 4), int(col_widths[3] - 12), int(row_height - 8)), Qt.AlignCenter | Qt.AlignVCenter, disp_text)
            y = total_y + row_height

            # 提示行
            note_y = y
            painter.fillRect(int(start_x), int(note_y), int(table_width), int(row_height), QColor('white'))
            pen2 = QPen(Qt.black)
            pen2.setWidth(1)
            painter.setPen(pen2)
            painter.drawRect(int(start_x), int(note_y), int(table_width), int(row_height))
            painter.setPen(default_pen)
            painter.drawText(QRect(int(start_x + 6), int(note_y + 6), int(table_width - 12), int(row_height - 8)), Qt.AlignLeft | Qt.AlignTop, "请确认您的缴费金额，如有疑问请咨询物业服务中心")
            y = note_y + row_height + 10

            # 底部签名
            painter.setFont(small_font)
            sig_height = row_height
            if is_wide_paper or is_narrow_paper:
                # 紧凑模式：紧跟内容
                sig_y = y
            else:
                # 标准模式：尝试置于底部，但确保不覆盖内容
                extra_pad = int(row_height * 0.3)
                bottom_y = int(page_rect.y() + (page_rect.height()) - max(margin_left, margin_right) - sig_height - extra_pad)
                sig_y = max(y + 10, bottom_y)
            left_x = int(start_x)
            right_x = int(start_x + table_width - int(table_width / 2))
            painter.drawText(QRect(left_x, int(sig_y), int(table_width / 2), 20), Qt.AlignLeft, "收款人：")
            painter.drawText(QRect(right_x, int(sig_y), int(table_width / 2), 20), Qt.AlignLeft, "收款单位盖章：")
        except Exception as e:
            print(f"_draw_merged_receipt 失败: {e}")
            raise

    def render_merged_receipt_to_image(self, payments, output_path, dpi=300):
        """将合并收据渲染为 PNG（payments 为 payment 对象列表）
        支持在调用时传入打印机可绘制宽度（通过 dpi 与 pageRect 计算并传递为 max_width_px），以保证渲染图片与打印机可绘制区域一致。
        """
        try:
            # 仅支持目标收据纸（241×93mm）
            w_mm, h_mm = self._target_w_mm, self._target_h_mm
            mm_per_inch = 25.4
            width_px = int(w_mm / mm_per_inch * dpi)
            height_px = int(h_mm / mm_per_inch * dpi)
            # 如果是宽纸且使用 300dpi，使用精确像素匹配物理打印测试（2847×1098）
            # 注意：不要对 dpi==300 做硬编码像素覆盖，调用者应传入 max_width_px 以匹配打印机可绘制区域
            # 计算顶部偏移与安全边距（像素）
            try:
                self._top_offset_px = int(self.top_offset_mm / mm_per_inch * dpi)
            except Exception:
                self._top_offset_px = 0
            try:
                self._safe_margin_px = int(self.safe_margin_mm / mm_per_inch * dpi)
            except Exception:
                self._safe_margin_px = 0

            image = QImage(width_px, height_px, QImage.Format_ARGB32)
            image.fill(Qt.white)
            painter = QPainter()
            painter.begin(image)
            page_rect = QRect(0, 0, width_px, height_px)
            self._draw_merged_receipt(painter, page_rect, payments)
            painter.end()
            ok = image.save(output_path)
            return ok
        except Exception as e:
            # 把异常向上抛出以便调用方能够获得详细错误信息用于调试
            raise

