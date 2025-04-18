"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/18 16:27
*  @FileName:   test_router_agent.py
**************************************
"""
import asyncio
import logging

from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow, ToolCallResult, AgentOutput, ToolCall
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore

from agents.router_agent import RouterAgent
from core.excel_table import ExcelTable
from openai_like_llm import OpenAILikeLLM, OPENAI_MODEL_NAME, OPENAI_API_BASE, OPENAI_API_KEY
from tools.quickchart_tool import generate_bar_chart, generate_pie_chart

# logging.basicConfig(level="DEBUG")


llm = OpenAILikeLLM(model=OPENAI_MODEL_NAME, api_base=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

# 是否上传了文档
is_uploaded = False

chat_store = SimpleChatStore()
chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=8000,
    chat_store=chat_store,
    chat_store_key="user",
)


async def run_agent(user_question, markdown):
    router_agent = RouterAgent(llm)
    agent_workflow = AgentWorkflow(
        agents=[router_agent.get_agent()],
        root_agent=router_agent.get_agent_name()
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

    print(f"最终结果：{final_output}")


if __name__ == '__main__':
    # 定义文件路径
    file_path = "../data/SuperStoreUS-2015.xlsx"

    # 判断文件扩展名
    excel_table = ExcelTable(file_path, merge_cells=False)
    markdown_text = excel_table.get_markdown_head()
    print(markdown_text)
    question = "这个表格是什么类型的"

    asyncio.run(run_agent(question, markdown_text))
