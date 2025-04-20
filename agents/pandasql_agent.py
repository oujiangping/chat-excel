"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 14:42
*  @FileName:   pandasql_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent

from core.agent import BaseAgent
from tools.quickchart_tool import generate_bar_chart, generate_pie_chart
from tools.table_tool import run_sql_queries, get_excel_info_tool


def get_sql_agent(llm):
    # 分析表格干什么的代理
    sql_table_agent = FunctionAgent(
        name="sql_table_agent",
        llm=llm,
        description="你是一个有用的正规表格分析助手",
        system_prompt=(
            """
            # 正规表格分析助手
            ## 功能描述
            你是一个专业的利用pandasql分析表格，并给出分析报告，也是数据洞察助手，擅长输出图文并茂的数据报告。

            ## 工具使用说明
            -  get_excel_info_tool 工具获取pandasql表格信息和表名可。
            - generate_bar_chart 工具用于生成条形图，generate_pie_chart 工具用于生成饼图，返回图片url请你自己插入正文
            - 对于分析的数据你应该考虑调用图形工具去生成图片并插入正文
            - run_sql_queries 工具用于执行 SQL 查询，返回查询结果。
            - 请你一定要使用图片工具去生成图片，不要自己乱生成。

            ## 注意事项
            - 根据用户提出的问题进行分析，生成严格遵守 SQLite3 SQL 规范的语句（可生成多条），避免执行出错。
            - 单个 SQL 查询语句的最大返回条数需控制在 20 条以内，防止单个查询返回过多数据。
            - 注意只要你分析出sql语句，就可以直接执行sql语句，不要去问客户端是否需要执行sql语句。
            - 注意每次执行前你都应该先调用 `get_excel_info_tool` 工具获取表格信息，当发生sql错误时你更加应该重新调用工具获取表信息，然后再根据表格信息生成sql语句。
            - 你应该正确的考虑使用什么图形化工具去生成图片（条形图好还是饼图好），不要一个劲的只使用一种。
            - 由于字段名会有空格，所以你需要使用反引号包裹字段名。
            - 所有的数据和图表应该都是采用工具得出，不能自己乱编造。

            # 输出要求
            - 仅回答与表格相关的问题，对于表格无关的问题请直接拒绝回答。
            - 依据表格中的数据，生成有针对性的统计分析建议。
            - 针对每个数据如果能够生成条形图应该都去调用一次工具去生成图片
            - 输出报告面向普通用户，sql语句只是你的工具功能，禁止报告中出现sql语句
            - 输出数据报告用Markdown格式，要图文并茂。
            - 不能无中生有乱造数据和图片。
            """

        ),
        tools=[run_sql_queries, get_excel_info_tool, generate_bar_chart, generate_pie_chart],
        verbose=True
    )
    return sql_table_agent


class SqlTableAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.agent = get_sql_agent(llm)
        self.get_agent()

    def get_agent(self):
        return self.agent

    def get_agent_name(self):
        return self.agent.name
