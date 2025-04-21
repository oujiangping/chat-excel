"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/21 16:13
*  @FileName:   test_re_parse_table_head.py
**************************************
"""
from core.excel_table import ExcelTable
from tools.analyze_tool import analyze_with_llm

if __name__ == '__main__':
    # 定义文件路径
    file_path = "../data/学生视力表.xls"
    excel_table = ExcelTable("../data/flightdata-head-hebing.xlsx", merge_cells=False)
    sheets_db = excel_table.get_sheets_db()
    df = sheets_db["flightdata"]
    print(df.head())
    # 重新定位表头
    row_index = 0
    print("位置0的数据:", df.iloc[0])  # 确认是否是Excel第一行（无效表头）
    header = df.iloc[row_index]
    print(f"header:{header}")
    df = df.iloc[row_index + 1:]
    # 设置新的表头
    df.columns = header
    df = df.reset_index(drop=True)
    sheets_db["flightdata"] = df
    print(f"重新定位表头成功，表名：flightdata, 新表头：{df.columns.tolist()}")
    print(df.head())

