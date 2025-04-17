import pandas as pd
from openpyxl import load_workbook
import xlrd


def load_excel(file_path, merge_cells=False):
    # 判断文件扩展名
    if file_path.endswith('.xlsx') or file_path.endswith('.xlsm') or file_path.endswith('.xltx') or file_path.endswith(
            '.xltm'):
        # 使用 openpyxl 打开 .xlsx 等格式文件
        wb = load_workbook(file_path)
        sheet_names = wb.sheetnames
        for sheet_name in sheet_names:
            sheet = wb[sheet_name]
            data = []
            for row in sheet.iter_rows(values_only=True):
                data.append(row)
            df = pd.DataFrame(data)
            print(df.to_markdown())
            print(f"工作表 {sheet_name} 的数据前几行：")
            print(df.head().to_csv(sep='\t', na_rep='nan'))
    elif file_path.endswith('.xls'):
        # 使用 xlrd 打开 .xls 格式文件
        workbook = xlrd.open_workbook(file_path)
        for sheet_name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(sheet_name)
            data = []
            for row in range(sheet.nrows):
                data.append(sheet.row_values(row))
            df = pd.DataFrame(data)
            print(df.to_markdown())
            print(f"工作表 {sheet_name} 的数据前几行：")
            print(df.head().to_csv(sep='\t', na_rep='nan'))
    else:
        print("不支持的文件格式，请使用 .xls 或 .xlsx 格式的文件。")