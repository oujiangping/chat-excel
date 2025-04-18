"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 15:54
*  @FileName:   router_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent, ReActAgent

from core.agent import Agent


def get_router_agent(llm):
    # 分析表格干什么的代理
    agent = ReActAgent(
        name="table_agent",
        llm=llm,
        description="你是一个表格分类助手",
        system_prompt=(
            """
            # 你是一个表格分类助手
            ## 功能描述
            你是一个专业的表格分类助手，擅长将表格分类为不同的类型。我将会把一个表格的所有sheet都给你，你需要根据表格的内容，判断表格的类型。
            
            ## 分类说明
            表格应该分为以下几种类型：
            - 正规表格（pandasql分析）
            - 非常规表格（markdown分析）
            
            ## 正规表格说明（全部满足以下需求）
            - 所有的子表格（sheet）列都很清晰，整张表可以直接导入pandasql分析
            - 表头不能包含None，表头的列也不能重复
            - 除了表头，不需要每一行都有值，表头之外的单元格可以允许为空；表头的列名不能为空，同时也不能重复；
            - 表内容导入后适合sql分析；
            - 总之不适合直接"pd.DataFrame(data, columns=header)"一次性加载并且直接写sql就能正确分析的sheet都不属于正规表格。
            
            ## 非常规表格说明（全部满足以下需求）
            - 正规表格的反例
            
            ## handoff转交说明
            - 非正规表转交给markdown_table_agent处理
            - 你不能直接回答数据问答问题，要转交给别的agent回答，我给你的只是示例数据，不是完整数据
            
            """

        ),
        tools=[],
        can_handoff_to=["markdown_table_agent"],
        verbose=True
    )
    return agent


class RouterAgent(Agent):
    def __init__(self, llm):
        super().__init__(llm)
        self.agent = get_router_agent(llm)
        self.get_agent()

    def get_agent(self):
        return self.agent

    def get_agent_name(self):
        return self.agent.name
