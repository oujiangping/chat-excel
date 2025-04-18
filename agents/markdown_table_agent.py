"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 14:13
*  @FileName:   markdown_table_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent

from core.agent import Agent
from tools.quickchart_tool import generate_bar_chart, generate_pie_chart


def get_markdown_table_agent(llm):
    # 分析表格干什么的代理
    markdown_table_agent = FunctionAgent(
        name="analyze_agent",
        llm=llm,
        description="你是一个有用的助手。",
        system_prompt=(
            """
            # 表格分析助手
            ## 功能描述
            你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出图文并茂的数据报告。

            ## 工具使用说明
            # 表格分析助手
            ## 功能描述
            你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出数据报告。

            ## 工具使用说明
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
            """

        ),
        tools=[generate_bar_chart, generate_pie_chart],
        verbose=True
    )
    return markdown_table_agent


class MarkdownTableAgent(Agent):
    def get_agent(self):
        return get_markdown_table_agent(self.llm)

    def get_agent_name(self):
        return "markdown_table_agent"
