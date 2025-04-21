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
        item_str = f"表格结构描述：\n表名:{sheet_name}\n{info_str}\n\n前几行数据(不是全部数据，数据应该单独执行sql查询，请勿直接用于计算最终结果，看看表头列名是不是不是第一行，如果不是你要清洗一下)：\n{head_str}\n\n----------------\n\n"
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


async def get_table_head_data_to_markdown(ctx: Context):
    """
    获取小部分表格信息与数据并返回结果，无需参数，返回表格数据和描述给智能体进行数据分析
    """
    excel_table = await ctx.get("table")
    return excel_table.get_markdown_head()


async def run_sql_queries(ctx: Context, queries: list[str]):
    """
    批量执行 SQL 查询并返回结果。
    参数:
    queries (str): 要执行的 SQL 查询语句列表。
    返回:
    返回序列化的执行结果
    """
    excel_table = await ctx.get("table")
    sheets_db = excel_table.get_sheets_db()
    results = ""
    for query in queries:
        try:
            print(f"执行 SQL 查询: {query}")
            sql_result = sqldf(query, sheets_db).to_csv(sep='\t', na_rep='nan')
            results += f"query: {query}, result: {sql_result}\n\n----------"
        except Exception as e:
            print(f"执行 SQL 查询时出错: {e}\n\n 现在我再次给你表格信息 {get_excel_info_head(sheets_db)} ， 请考虑是不是现在表头错了，请你重新定位表头，然后再执行sql查询")
            results += f"query: {query}, result: 执行 SQL 查询时出错。{e}\n\n----------"
    return results


async def get_excel_info_tool(ctx: Context):
    """
    获取表格结构和示例数据
    返回:
    str: 获取表格结构和示例数据。
    """
    excel_table = await ctx.get("table")
    sheets_db = excel_table.get_sheets_db()
    """
    获取表格结构和示例数据
    返回:
    str: 获取表格结构和示例数据。
    """
    return get_excel_info_head(sheets_db)


async def re_parse_table_head(ctx: Context, sheet_name: str, row_index: int):
    """
    根据表格信息，重新指向正确字段名所在的行的工具row_index必须大于1
    参数:
    sheet_name (str): 表名(sheet_name)
    row_index (int): 重新把表头指向row_index作为有效表头所在的第N行
    因为如果现在第1行如果就是表头，那么就不需要重新定位表头了，所以row_index必须大于1
    """
    excel_table = await ctx.get("table")
    sheets_db = excel_table.get_sheets_db()
    if row_index <= 1:
        return "表头所在的行索引必须大于1"
    row_index -= 2
    if sheet_name in sheets_db:
        df = sheets_db[sheet_name]
        # 重新定位表头
        df.columns = df.iloc[row_index]
        df = df.iloc[row_index + 1:]
        df = df.reset_index(drop=True)
        sheets_db[sheet_name] = df
        excel_table.set_sheets_db(sheets_db)
        await ctx.set("table", excel_table)
        print(f"重新定位表头成功，表名：{sheet_name}, 新表头：{df.columns.tolist()}")
        return f"重新定位表头成功，表名：{sheet_name}, 新表头：{df.columns.tolist()}"

    return "没找到sheet表格"
