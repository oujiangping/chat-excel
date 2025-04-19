"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 14:45
*  @FileName:   Agent.py
**************************************
"""


class BaseAgent:
    def __init__(self, llm):
        self.llm = llm
        self.agent = None

    # 定义一个虚函数 其它类必须继承
    def get_agent(self):
        raise NotImplementedError("get_agent() 方法必须在子类中实现")

    def get_agent_name(self):
        raise NotImplementedError("get_agent_name() 方法必须在子类中实现")
