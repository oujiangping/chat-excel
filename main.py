import gradio as gr
from llama_index.core.agent.workflow import AgentWorkflow, ToolCallResult, AgentOutput, ToolCall
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.workflow import Context

from agents.markdown_table_agent import MarkdownTableAgent
from agents.pandasql_agent import SqlTableAgent
from agents.router_agent import RouterAgent
from core.excel_table import ExcelTable
from utils.export_tools import export_to_markdown
from core.openai_like_llm import OpenAILikeLLM, OPENAI_MODEL_NAME, OPENAI_API_BASE, OPENAI_API_KEY
from tools.table_tool import get_all_table_names
from view.view import get_loading_view

# logging.basicConfig(level="DEBUG")


llm = OpenAILikeLLM(model=OPENAI_MODEL_NAME, api_base=OPENAI_API_BASE, api_key=OPENAI_API_KEY)
llm_function = OpenAILikeLLM(model=OPENAI_MODEL_NAME, api_base=OPENAI_API_BASE, api_key=OPENAI_API_KEY)

# 是否上传了文档
is_uploaded = False
excel_table = None

chat_store = SimpleChatStore()
chat_memory = ChatMemoryBuffer.from_defaults(
    token_limit=8000,
    chat_store=chat_store,
    chat_store_key="user",
)


async def analyze_question(question):
    global is_uploaded
    global excel_table
    if not is_uploaded:
        gr.Warning("请先上传Excel文件")
        yield "请先上传Excel文件", ""
        return

    router_agent = RouterAgent(llm_function)
    markdown_table_agent = MarkdownTableAgent(llm)
    sql_agent = SqlTableAgent(llm)
    agent_workflow = AgentWorkflow(
        agents=[router_agent.get_agent(), markdown_table_agent.get_agent(), sql_agent.get_agent()],
        root_agent=router_agent.get_agent_name(),
    )

    ctx = Context(agent_workflow)
    await ctx.set("table", excel_table)
    # 当前工具调用次数
    call_count = 0

    handler = agent_workflow.run(
        user_msg=f'''
        ### 用户问题
        {question}
        ''',
        memory=chat_memory,
        ctx=ctx
    )

    current_agent = None
    final_output = ""
    router_output = ""
    thinking_msg_output = "## 任务执行\n"

    async for event in handler.stream_events():
        if (
                hasattr(event, "current_agent_name")
                and event.current_agent_name != current_agent
        ):
            current_agent = event.current_agent_name
            thinking_msg = f"\n{'=' * 50}\n🤖 Agent: {current_agent}\n{'=' * 50}\n"
            print(thinking_msg)
            thinking_msg_output += f"#### 🤖执行agent: {current_agent}\n"
            yield thinking_msg_output, final_output
        elif isinstance(event, AgentOutput):
            if event.response.content:
                thinking_msg = f"📤 Output: {event.response.content}"
                print(thinking_msg)
                if current_agent == "sql_table_agent" or current_agent == "markdown_table_agent":
                    final_output += event.response.content
                else:
                    router_output += event.response.content
            if event.tool_calls:
                tool_msg = f"🛠️  Planning to use tools: {[call.tool_name for call in event.tool_calls]}"
                thinking_msg_output += f"🛠️  Planning to use tools: {[call.tool_name for call in event.tool_calls]}\n"
                print(tool_msg)
                yield thinking_msg_output, final_output
        elif isinstance(event, ToolCallResult):
            tool_result_msg = (
                f"🔧 Tool Result ({event.tool_name}):\n"
                f"  Arguments: {event.tool_kwargs}\n"
                f"  Output: {event.tool_output}"
            )
            print(tool_result_msg)
            thinking_msg_output += f"#### 🔧工具调用结束: {event.tool_name}\n"
            yield thinking_msg_output, final_output
        elif isinstance(event, ToolCall):
            if call_count > 10:
                thinking_msg_output += f"##### 🛑 出现了点异常，达到最大调用次数，停止调用工具 \n"
                yield thinking_msg_output, final_output
                return
            tool_call_msg = (
                f"🔨 Calling Tool: {event.tool_name}\n"
                f"  With arguments: {event.tool_kwargs}"
            )
            print(tool_call_msg)
            thinking_msg_output += f"#### 🔧工具调用开始: {event.tool_name}\n"
            yield thinking_msg_output, final_output
    if final_output == "":
        yield "", router_output
    else:
        yield "", final_output


async def start_async_analysis(question):
    yield gr.update(visible=True), "数据处理中", gr.update(visible=True)
    async for thinking_output_str, result_str in analyze_question(question):
        yield gr.update(value=thinking_output_str), result_str, gr.update(visible=True)
    yield gr.update(visible=False), result_str, gr.update(visible=False)


def load_excel(file):
    global is_uploaded
    global excel_table

    excel_table = ExcelTable(file)
    print(excel_table.get_markdown_head())

    print(
        f"成功加载 {len(excel_table.get_sheets_db())} 个工作表: {', '.join(get_all_table_names(excel_table.get_sheets_db()))}")

    is_uploaded = True

    return "Excel 文件已成功加载。"


with gr.Blocks() as excel_view:
    gr.Markdown("### Excel 表格分析系统")
    with gr.Row():
        with gr.Column():
            file_input = gr.File(label="选择 Excel 文件")
            load_output = gr.Textbox(label="文件加载结果")
            question_input = gr.Textbox(label="请输入问题", placeholder="输入你的问题")

        with gr.Column():
            # 加一个模块现实实时思考产生的内容
            thinking_output = gr.Markdown(label="思考过程")
            answer_output = gr.Markdown(label="分析结果")
            # Replace Spinner with a hidden textbox to simulate loading state
            loading_indicator = gr.Textbox(visible=False, value="Loading...")
            # 添加 文件 导出按钮
            export_button = gr.Button("导出为 Markdown")
            export_button.click(
                fn=export_to_markdown,
                inputs=answer_output,
                outputs=gr.File(label="导出的 Markdown 文件")
            )

    loading_message = get_loading_view()
    # gr.processing_utils.send_custom_event(showLoading_js)  # 显示加载弹框
    file_input.upload(load_excel, inputs=file_input, outputs=load_output)
    # Modify the submit call to add loading state control
    question_input.submit(
        fn=start_async_analysis,
        inputs=question_input,
        outputs=[thinking_output, answer_output, loading_message],
        queue=True
    )

if __name__ == "__main__":
    excel_view.launch()
