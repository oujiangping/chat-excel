import logging

from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow, ToolCallResult, AgentOutput, ToolCall
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore

from core.excel_table import ExcelTable
from core.openai_like_llm import OpenAILikeLLM, OPENAI_MODEL_NAME, OPENAI_API_BASE, OPENAI_API_KEY
from tools.quickchart_tool import generate_bar_chart, generate_pie_chart

logging.basicConfig(level="DEBUG")


llm = OpenAILikeLLM(model=OPENAI_MODEL_NAME, api_base=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

# 是否上传了文档
is_uploaded = False

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
    memory=chat_memory,
    verbose=True
)


async def run_agent(user_question, markdown):
    agent_workflow = AgentWorkflow(
        agents=[analyze_agent],
        root_agent=analyze_agent.name,
    )

    handler = agent_workflow.run(
        user_msg=f'''
        ### 用户问题
        {user_question}
    
        ### 表格数据
        {markdown}
        ''',
        memory=chat_memory
    )

    current_agent = None
    final_output = ""
    router_output = ""
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
            else:
                router_output += event.response.content
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

    print(f"最终结果：{final_output}")


if __name__ == '__main__':
    # 定义文件路径
    file_path = "../data/score.xlsx"

    # 判断文件扩展名
    excel_table = ExcelTable(file_path, merge_cells=False)
    markdown_text = excel_table.show_markdown()
    question = "请分析学生视力变化并且给我一份报告"

    # asyncio.run(run_agent(question, markdown_text))
