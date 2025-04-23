"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/23 13:31
*  @FileName:   test_extract_table_names.py
**************************************
"""
from pandasql.sqldf import extract_table_names

result = extract_table_names('SELECT MAX(`Temp`) FROM `df` LIMIT 20;')
print(result)
