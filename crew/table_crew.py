"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/19 11:27
*  @FileName:   TableCrew.py
**************************************
"""
from crewai import Agent, Crew, Task, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from crewai.tools import tool

from core.excel_table import ExcelTable


@CrewBase
class TableCrew:
    """
    处理表格并出具报告的crew
    """
    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self, file_path):
        self.file_path = file_path

    @agent
    def router_agent(self) -> Agent:
        return Agent(
            role="表格分类助手。",
            goal="""
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
            
            """,
            backstory="你是一个专业的表格分类助手，擅长将表格分类为不同的类型。我将会把一个表格的所有sheet都给你，你需要根据表格的内容，判断表格的类型。",
            memory=True,  # Enable memory
            tools=[self.get_table_data_to_markdown],
            verbose=True,
            allow_delegation=True,
            max_rpm=None,  # No limit on requests per minute
            max_iter=20,  # Default value for maximum iterations
        )

    @tool
    async def get_table_data_to_markdown(self):
        """
        获取表格信息与数据并返回结果，无需参数，返回表格数据和描述给智能体进行数据分析
        """
        excel_table = ExcelTable(self.file_path)
        return excel_table.get_markdown()

    @task
    def table_report_task(self) -> Task:
        return Task(
            description="分析表格的分类，根据表格的分类，选择合适的agent来处理表格。",
            expected_output="根据用户的问题选择合适的工具和代理来处理问题，同时结合上下文使用用户的语言回答问题。",
            verbose=True,
            agent=self.router_agent(),
            human_input=True
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,  # Automatically collected by the @agent decorator
            tasks=self.tasks,    # Automatically collected by the @task decorator.
            process=Process.sequential,
            verbose=True,
        )

