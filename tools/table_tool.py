"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/15 14:39
*  @FileName:   excel_tool.py
**************************************
"""
import io

from llama_index.core.workflow import Context
from pandasql import sqldf

sheets_db = {}  # {sheet_name: DataFrame}


def is_regular_table(df):
    markdown_text = df.to_markdown()
    print(markdown_text)
    if df.empty:
        print(f"包含空表")
        return False

    # 取出第一行
    columns = df.columns.tolist()
    print(columns)

    # # 处理合并单元格
    # df = df.ffill()

    markdown_text = df.to_markdown()
    print(markdown_text)

    return True


# 合并单元格的函数
def merge_cells(df):
    # 合并行
    df = df.ffill()
    return df


def get_all_table_names(db):
    """获取所有已加载的表名（工作表名）"""
    return list(db.keys())


def get_excel_description(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    buffer.close()
    return info_str


def get_excel_info_head(db):
    description = ""
    # 获取表结构描述
    # 将字典中的 DataFrame 分配变量名（例如表名）
    for sheet_name, df in db.items():
        info_str = get_excel_description(df)
        head_str = df.head().to_csv(sep='\t', na_rep='nan')
        item_str = f"表格结构描述：\n表名:{sheet_name}\n{info_str}\n\n前几行数据(不是全部数据，数据应该单独执行sql查询，请勿直接用于计算最终结果)：\n{head_str}\n\n----------------\n\n"
        description += item_str
    return description


# 测试执行表是否有问题
def test_run_sql_queries(db):
    for sheet_name, df in db.items():
        try:
            print("开始测试表：", sheet_name)
            query = f"select * from {sheet_name} limit 1"
            sql_result = sqldf(query, db).to_csv(sep='\t', na_rep='nan')
            print(f"结束测试表：{sheet_name}，结果：{sql_result}")
        except Exception as e:
            print(f"测试表：{sheet_name} 时出错: {e}")
            return False
    return True


async def get_table_data_to_markdown(ctx: Context):
    """
    获取表格信息与数据并返回结果，无需参数，返回表格数据和描述给智能体进行数据分析
    """
    excel_table = await ctx.get("table")
    return excel_table.get_markdown()


def run_sql_queries(queries: list[str]):
    """
    批量执行 SQL 查询并返回结果。
    参数:
    queries (str): 要执行的 SQL 查询语句列表。
    返回:
    返回序列化的执行结果
    """
    global sheets_db
    results = ""
    for query in queries:
        try:
            print(f"执行 SQL 查询: {query}")
            sql_result = sqldf(query, sheets_db).to_csv(sep='\t', na_rep='nan')
            results += f"query: {query}, result: {sql_result}\n\n----------"
        except Exception as e:
            print(f"执行 SQL 查询时出错: {e}\n\n 现在我再次给你表格信息 {get_excel_info_head(sheets_db)}")
            results += f"query: {query}, result: 执行 SQL 查询时出错。{e}\n\n----------"
    return results


def get_excel_info_tool():
    """
    获取表格结构和示例数据
    返回:
    str: 获取表格结构和示例数据。
    """
    global sheets_db
    """
    获取表格结构和示例数据
    返回:
    str: 获取表格结构和示例数据。
    """
    return get_excel_info_head(sheets_db)


def set_sheets_db(db):
    global sheets_db
    sheets_db = db


def clear_sheets_db():
    global sheets_db
    sheets_db.clear()


def get_sheets_db():
    global sheets_db
    return sheets_db
