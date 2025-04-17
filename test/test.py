import pandas as pd
from openpyxl import load_workbook
import xlrd

from utils.excel_loader import load_excel

# 定义文件路径
file_path = "../data/学生视力表.xls"

# 判断文件扩展名
load_excel(file_path)