"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 15:54
*  @FileName:   router_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent

from core.agent import BaseAgent
from tools.table_tool import get_table_head_data_to_markdown


def get_router_agent(llm):
    # 分析表格干什么的代理
    agent = FunctionAgent(
        name="table_agent",
        llm=llm,
        description="你是一个表格分类助手，表格数据我传到get_table_head_data_to_markdown这个工具了你去拿",
        system_prompt=(
            """
            # 你是一个表格分类助手
            ## 功能描述
            你是一个专业的表格分类助手，擅长将表格分类为不同的类型。我将会把一个表格的所有sheet都给你，你需要根据表格的内容，判断表格的类型，并给出充分的理由。表格数据我传到get_table_head_data_to_markdown这个工具了你去拿。
            
            ## 分类说明
            表格应该分为以下几种类型：
            - 正规表格（sql分析）
            - 非常规表格（markdown分析）
            
            ## 表格示例数据来源
            - 表格示例数据来源是get_table_head_data_to_markdown工具获取的部分数据（不完整），你需要根据表格的内容，判断表格的类型。
            
            ## 正规表格说明（全部满足以下需求）
            - 所有的子表格（sheet）列都很清晰，整张表可以直接或者简单的去掉几行后就可以导入pandasql分析
            - 除了表头，不需要每一行都有值，表头之外的单元格可以允许为空；表头的列名不能为空，同时也不能重复；
            - 表内容导入后适合sql分析；
            - 总之不适合直接"pd.DataFrame(data, columns=header)"一次性加载并且直接写sql就能正确分析的sheet都不属于正规表格。
            - 如果去掉不正规的表头，剩下的表格内容就正规了，可以直接导入pandas分析，那也算正规表。
            - 如果列名字段名重复会导致转化成sql时会报错，所以应该当作非正规表格对待
            
            ## 非常规表格说明（全部满足以下需求）
            - 正规表格的反例
            
            ## handoff转交说明
            - 非正规表转交给markdown_table_agent处理
            - 正规表转交给sql_table_agent处理
            - 你不能直接处理和分析表格数据，因为你的任务是判断表格的类型，而不是分析表格数据。
            
            """

        ),
        tools=[get_table_head_data_to_markdown],
        can_handoff_to=["markdown_table_agent", "sql_table_agent"],
        verbose=True
    )
    return agent


class RouterAgent(BaseAgent):
    def __init__(self, llm):
        super().__init__(llm)
        self.agent = get_router_agent(llm)
        self.get_agent()

    def get_agent(self):
        return self.agent

    def get_agent_name(self):
        return self.agent.name
