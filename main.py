import asyncio
import io
import os

import pandas as pd
from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow, ToolCallResult, AgentOutput, ToolCall
from llama_index.core.base.llms.types import LLMMetadata, MessageRole
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.llms.openai import OpenAI
from pandasql import sqldf

from tools.quickchart_tool import generate_bar_chart, generate_pie_chart

# logging.basicConfig(level="DEBUG")

CONTEXT_WINDOW = 128000

print("所有环境变量：")
for key, value in os.environ.items():
    print(f"{key}: {value}")

# 如果没有设置环境变量，报错
if "OPENAI_API_BASE" not in os.environ:
    raise ValueError("OPENAI_API_BASE 环境变量未设置")

OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_MODEL_NAME = os.environ["OPENAI_MODEL_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]


class OpenAILikeLLM(OpenAI):
    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=CONTEXT_WINDOW,
            num_output=self.max_tokens or -1,
            is_chat_model=True,
            is_function_calling_model=True,
            model_name=self.model,
            system_role=MessageRole.SYSTEM,
        )


llm = OpenAILikeLLM(model=OPENAI_MODEL_NAME, api_base=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

sheets_db = {}  # {sheet_name: DataFrame}


def get_all_table_names():
    """获取所有已加载的表名（工作表名）"""
    return list(sheets_db.keys())


def is_regular_table(df):
    """
    判断表格是否为正规表格
    这里的判断标准是：
    1. 没有合并单元格（假设用缺失值代表合并单元格）
    2. 表头和数据类型一致，且没有空列或空行
    """
    # 检查是否有合并单元格
    # 检查是否有缺失值（合并单元格可能导致缺失值）
    if df.isnull().any().any():
        return False
    # 检查是否有空列或空行
    if df.dropna(how='all', axis=0).shape != df.shape or df.dropna(how='all', axis=1).shape != df.shape:
        return False
    return True


# 获取表格描述
def get_excel_description(df):
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_str = buffer.getvalue()
    buffer.close()
    return info_str


# 批量查询sql工具 入参是list[str]
async def run_sql_queries(queries: list[str]):
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
            # 替换换行符为空格
            # query = query.replace('\\\n', ' ')
            print(f"执行 SQL 查询: {query}")
            sql_result = sqldf(query, globals()).to_csv(sep='\t', na_rep='nan')
            results += f"query: {query}, result: {sql_result}\n\n----------"
        except Exception as e:
            print(f"执行 SQL 查询时出错: {e}")
            results += f"query: {query}, result: 执行 SQL 查询时出错。{e}\n\n----------"
    return results


def get_excel_info():
    """
    获取表格结构和示例数据
    返回:
    str: 获取表格结构和示例数据。
    """
    global sheets_db
    description = ""
    # 获取表结构描述
    # 将字典中的 DataFrame 分配变量名（例如表名）
    for sheet_name, df in sheets_db.items():
        info_str = get_excel_description(df)
        head_str = df.head().to_csv(sep='\t', na_rep='nan')
        item_str = f"表格结构描述：\n表名:{sheet_name}\n{info_str}\n\n前几行数据(不是全部数据，数据应该单独执行sql查询，请勿直接用于计算最终结果)：\n{head_str}\n\n----------------\n\n"
        description += item_str
    return description


chat_store = SimpleChatStore()
chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=8000,
    chat_store=chat_store,
    chat_store_key="user",
)

# 分析表格干什么的代理
analyze_agent = FunctionAgent(
    name="analyze_agent",
    llm=llm,
    description="你是一个有用的助手。",
    system_prompt=(
        """
        # 表格分析助手
        ## 功能描述
        你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出数据报告。
        
        ## 工具使用说明
        # 表格分析助手
        ## 功能描述
        你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出数据报告。
        
        ## 工具使用说明
        -  get_excel_info 工具获取pandasql表格信息和表名可。
        - generate_bar_chart 工具用于生成条形图，generate_pie_chart 工具用于生成饼图，返回图片url请你自己插入正文
        - 对于分析的数据你应该考虑调用图形工具去生成图片并插入正文
        - run_sql_queries 工具用于执行 SQL 查询，返回查询结果。
        
        ## 注意事项
        - 根据用户提出的问题进行分析，生成严格遵守 SQLite3 SQL 规范的语句（可生成多条），避免执行出错。
        - 单个 SQL 查询语句的最大返回条数需控制在 20 条以内，防止单个查询返回过多数据。
        - 注意只要你分析出sql语句，就可以直接执行sql语句，不要去问客户端是否需要执行sql语句。
        - 注意每次执行前你都应该先调用 `get_excel_info` 工具获取表格信息，当发生sql错误时你更加应该重新调用工具获取表信息，然后再根据表格信息生成sql语句。
        - 你应该正确的考虑使用什么图形化工具去生成图片（条形图好还是饼图好），不要一个劲的只使用一种。
        - 由于字段名会有空格，所以你需要使用反引号包裹字段名。
        
        # 输出要求
        - 仅回答与表格相关的问题，对于表格无关的问题请直接拒绝回答。
        - 依据表格中的数据，生成有针对性的统计分析建议。
        - 针对每个数据如果能够生成条形图应该都去调用一次工具去生成图片
        - 输出报告面向普通用户，sql语句只是你的工具功能，禁止报告中出现sql语句
        - 输出数据报告用Markdown格式，要图文并茂。
        """

    ),
    tools=[run_sql_queries, get_excel_info, generate_bar_chart, generate_pie_chart],
    memory=chat_memory,
    verbose=True
)


# 定义主函数
async def main():
    """
    主函数，负责读取 Excel 文件，处理用户输入的问题。
    """
    global sheets_db
    # 读取 Excel 文件
    # file_path = input("请输入 Excel 文件的路径: ")
    file_path = "data/SuperStoreUS-2015.xlsx"
    sheets_db = pd.read_excel(file_path, sheet_name=None)
    print(f"成功加载 {len(sheets_db)} 个工作表: {', '.join(get_all_table_names())}")
    # 验证表格规范性（可选）
    for sheet_name, df in sheets_db.items():
        if not is_regular_table(df):
            print(f"警告：工作表 {sheet_name} 包含不规则格式,停止解析")

    # 将字典中的 DataFrame 分配变量名（例如表名）
    for sheet_name, df in sheets_db.items():
        globals()[sheet_name] = df  # 动态创建变量（如 orders、customers）
    info_str = get_excel_info()
    # 打印 DataFrame 的信息和前几行数据
    print(info_str)
    while True:
        question = input("请输入问题（输入 'exit' 退出）: ")
        if question.lower() == 'exit':
            break

        agent_workflow = AgentWorkflow(
            agents=[analyze_agent],
            root_agent=analyze_agent.name,
        )

        # draw_all_possible_flows(agent_workflow, filename="basic_workflow.html")

        handler = agent_workflow.run(
            user_msg=question,
            memory=chat_memory
        )
        current_agent = None
        current_tool_calls = ""
        final_output = "--------------------------------------------------\n"
        async for event in handler.stream_events():
            if (
                    hasattr(event, "current_agent_name")
                    and event.current_agent_name != current_agent
            ):
                current_agent = event.current_agent_name
                print(f"\n{'=' * 50}")
                print(f"🤖 Agent: {current_agent}")
                print(f"{'=' * 50}\n")
            elif isinstance(event, AgentOutput):
                if event.response.content:
                    print("📤 Output:", event.response.content)
                    final_output += event.response.content
                if event.tool_calls:
                    print(
                        "🛠️  Planning to use tools:",
                        [call.tool_name for call in event.tool_calls],
                    )
            elif isinstance(event, ToolCallResult):
                print(f"🔧 Tool Result ({event.tool_name}):")
                print(f"  Arguments: {event.tool_kwargs}")
                print(f"  Output: {event.tool_output}")
            elif isinstance(event, ToolCall):
                print(f"🔨 Calling Tool: {event.tool_name}")
                print(f"  With arguments: {event.tool_kwargs}")
        print(final_output)


if __name__ == "__main__":
    asyncio.run(main())
