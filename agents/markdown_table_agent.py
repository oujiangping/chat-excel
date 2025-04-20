"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 14:13
*  @FileName:   markdown_table_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent

from core.agent import BaseAgent
from tools.analyze_tool import analyze_table
from tools.quickchart_tool import generate_bar_chart, generate_pie_chart
from tools.table_tool import get_table_data_to_markdown


def get_markdown_table_agent(llm):
    # 分析表格干什么的代理
    markdown_table_agent = FunctionAgent(
        name="markdown_table_agent",
        llm=llm,
        description="你是一个有用的非正规表格分析助手。",
        system_prompt=(
            """
            # 非正规表格分析助手
            ## 功能描述
            你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出图文并茂的数据报告。

            ## 工具使用说明
            - analyze_tool 工具用于分析表格数据，返回分析结果,你应该使用这个工具去分析表格数据不需要你自己分析
            - 在收到analyze_tool的结果后你使用你需要对报告进行整理结合图形化工具生成图片并插入正文
            - generate_bar_chart 工具用于生成条形图，generate_pie_chart 工具用于生成饼图，返回图片url请你自己插入正文
            - 对于分析的数据你应该考虑调用图形工具去生成图片并插入正文
            - 请你一定要使用图片工具去生成图片，不要自己乱生成。

            ## 注意事项
            - 你应该正确的考虑使用什么图形化工具去生成图片（条形图好还是饼图好），不要一个劲的只使用一种。
            - 所有的数据和图表不能自己乱编造。

            # 输出要求
            - 仅回答与表格相关的问题，对于表格无关的问题请直接拒绝回答。
            - 依据表格中的数据，生成有针对性的统计分析建议。
            - 针对每个数据如果能够生成条形图应该都去调用一次工具去生成图片
            - 输出数据报告用Markdown格式，要图文并茂。
            - 不能无中生有乱造数据和图片。
            - 尽量文字结合图片回答，不要能生成图片却不生成图片，可以多次使用图形工具
            """

        ),
        tools=[analyze_table, generate_bar_chart, generate_pie_chart],
        verbose=True
    )
    return markdown_table_agent


class MarkdownTableAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.agent = get_markdown_table_agent(llm)
        self.get_agent()

    def get_agent(self):
        return self.agent

    def get_agent_name(self):
        return self.agent.name

