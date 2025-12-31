#!/usr/bin/env python3
"""
生成住户导入模板文件（Excel .xlsx）

用法：
    python scripts/generate_import_template_file.py

将会在项目根目录和 ./exports/ 中各生成一个名为 "住户导入模板.xlsx" 的文件（会覆盖同名文件）。
"""
import os
import sys

from utils.excel_importer import ExcelImporter


def ensure_exports_dir():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    exports_dir = os.path.join(base, 'exports')
    if not os.path.exists(exports_dir):
        try:
            os.makedirs(exports_dir, exist_ok=True)
        except Exception as e:
            print(f"无法创建 exports 目录：{e}", file=sys.stderr)
            return None
    return exports_dir


def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    root_template = os.path.join(base_dir, '住户导入模板.xlsx')
    exports_dir = ensure_exports_dir()
    exports_template = os.path.join(exports_dir, '住户导入模板.xlsx') if exports_dir else None

    try:
        ExcelImporter.create_import_template(root_template)
        print(f"已在项目根目录生成模板：{root_template}")
    except Exception as e:
        print(f"生成根目录模板失败：{e}", file=sys.stderr)

    if exports_template:
        try:
            ExcelImporter.create_import_template(exports_template)
            print(f"已在 exports/ 目录生成模板：{exports_template}")
        except Exception as e:
            print(f"生成 exports 模板失败：{e}", file=sys.stderr)


if __name__ == '__main__':
    main()


