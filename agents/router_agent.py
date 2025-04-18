"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 15:54
*  @FileName:   router_agent.py
**************************************
"""
from llama_index.core.agent.workflow import FunctionAgent

from core.agent import Agent


def get_router_agent(llm):
    # 分析表格干什么的代理
    agent = FunctionAgent(
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
            - 所有的子表（sheet）格行列都很清晰，这类表格一般就像mysql的表一样比较方正，适合sql分析，可以直接使用pandasql进行分析。
            - 一个sheet里面只能包含一个表格，不能包含多个表格（因为没法在不经过处理的情况下直接弄到pandasql里面，即使可以也是错的）
            - 那种表头就是合并行或者不是直接是列名的表格，都不适合sql分析。
            - 列名不能为空值和重复
            - 适合进行数据分析
            - 总之不适合直接"pd.DataFrame(data, columns=header)"一次性加载并且直接写sql就能正确分析的sheet都不属于正规表格。
            
            ## 非常规表格说明（全部满足以下需求）
            - 正规表格的反例
            
            """

        ),
        tools=[],
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
