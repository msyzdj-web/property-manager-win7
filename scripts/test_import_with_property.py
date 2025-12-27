#!/usr/bin/env python3
"""
生成包含 identity/property_type 的测试 Excel 并调用导入器执行导入，结果写入 exports/import_result.txt
运行： python3 scripts/test_import_with_property.py
"""
import os
from datetime import datetime
import openpyxl

from utils.excel_importer import ExcelImporter

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
EXPORTS = os.path.join(ROOT, 'exports')
os.makedirs(EXPORTS, exist_ok=True)

TEST_XLSX = os.path.join(EXPORTS, 'test_import_with_property.xlsx')
RESULT_TXT = os.path.join(EXPORTS, 'import_result.txt')

def create_test_file():
    wb = openpyxl.Workbook()
    sh = wb.active
    headers = ['房号', '姓名', '电话', '面积', '入住日期', '身份(identity)', '房屋类型(property_type)']
    sh.append(headers)
    sh.append(['1-1-900', '测试A', '13800000001', 80.0, '2024-01-01', '房主', '住宅'])
    sh.append(['1-1-901', '测试B', '13800000002', 50.0, '2024-02-01', '租户', '商铺'])
    sh.append(['1-1-902', '测试C', '', 60.0, '', '', ''])  # use defaults
    wb.save(TEST_XLSX)
    print("已生成测试文件：", TEST_XLSX)

def run_import():
    try:
        success, fail, errors = ExcelImporter.import_residents(TEST_XLSX)
        with open(RESULT_TXT, 'w', encoding='utf-8') as f:
            f.write(f"成功: {success}\\n失败: {fail}\\n")
            if errors:
                f.write("错误详情:\\n")
                for e in errors:
                    f.write(e + "\\n")
        print("导入完成，结果保存到：", RESULT_TXT)
    except Exception as e:
        with open(RESULT_TXT, 'w', encoding='utf-8') as f:
            f.write("导入异常: " + str(e))
        print("导入异常，详情写入：", RESULT_TXT)

if __name__ == '__main__':
    create_test_file()
    run_import()


