"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 11:00
*  @FileName:   excel_table.py
**************************************
"""
# excel文件类

from utils.excel_loader import load_excel_from_file


class ExcelTable:
    def __init__(self, file_path, merge_cells=False):
        self.file_path = file_path
        self.merge_cells = merge_cells
        self.sheets_db = load_excel_from_file(file_path, merge_cells)

    def set_sheets_db(self, sheets_db):
        self.sheets_db = sheets_db

    def is_regular_table(self):
        """判断是否是常规表格"""
        for sheet_name, df in self.sheets_db.items():
            if not df.empty:
                return True

    def show_markdown(self):
        """展示表格"""
        print(self.get_markdown())

    def get_markdown(self):
        """展示表格"""
        markdown_text = ""
        for sheet_name, df in self.sheets_db.items():
            markdown_text += f"## 表格(sheet)名称: {sheet_name}\n"
            markdown_text += df.to_markdown() + "\n\n"
        return markdown_text

    # 获取markdown格式前100行
    def get_markdown_head(self):
        """展示表格"""
        markdown_text = ""
        for sheet_name, df in self.sheets_db.items():
            markdown_text += f"## 表格(sheet)名称: {sheet_name}\n"
            markdown_text += df.head(20).to_markdown() + "\n\n"
        return markdown_text

    def get_sheets_db(self):
        return self.sheets_db

