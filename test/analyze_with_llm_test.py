from core.excel_table import ExcelTable
from tools.analyze_tool import analyze_with_llm

if __name__ == '__main__':
    # 定义文件路径
    file_path = "../data/学生视力表.xls"
    excel_table = ExcelTable("../data/学生视力表.xls", merge_cells=False)
    result = analyze_with_llm(excel_table.get_markdown(), "请分析一下数据并给我报告")
    print(result)
