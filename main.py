import gradio as gr
import pandas as pd
from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow, ToolCallResult, AgentOutput, ToolCall
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore

from export_tools import export_to_markdown
from openai_like_llm import OpenAILikeLLM, OPENAI_MODEL_NAME, OPENAI_API_BASE, OPENAI_API_KEY
from tools.table_tool import run_sql_queries, clear_sheets_db, set_sheets_db, get_excel_info_tool, \
    get_all_table_names, get_sheets_db, get_global, is_regular_table
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
        -  get_excel_info_tool 工具获取pandasql表格信息和表名可。
        - generate_bar_chart 工具用于生成条形图，generate_pie_chart 工具用于生成饼图，返回图片url请你自己插入正文
        - 对于分析的数据你应该考虑调用图形工具去生成图片并插入正文
        - run_sql_queries 工具用于执行 SQL 查询，返回查询结果。
        - 请你一定要使用图片工具去生成图片，不要自己乱生成。

        ## 注意事项
        - 根据用户提出的问题进行分析，生成严格遵守 SQLite3 SQL 规范的语句（可生成多条），避免执行出错。
        - 单个 SQL 查询语句的最大返回条数需控制在 20 条以内，防止单个查询返回过多数据。
        - 注意只要你分析出sql语句，就可以直接执行sql语句，不要去问客户端是否需要执行sql语句。
        - 注意每次执行前你都应该先调用 `get_excel_info_tool` 工具获取表格信息，当发生sql错误时你更加应该重新调用工具获取表信息，然后再根据表格信息生成sql语句。
        - 你应该正确的考虑使用什么图形化工具去生成图片（条形图好还是饼图好），不要一个劲的只使用一种。
        - 由于字段名会有空格，所以你需要使用反引号包裹字段名。
        - 所有的数据和图表应该都是采用工具得出，不能自己乱编造。

        # 输出要求
        - 仅回答与表格相关的问题，对于表格无关的问题请直接拒绝回答。
        - 依据表格中的数据，生成有针对性的统计分析建议。
        - 针对每个数据如果能够生成条形图应该都去调用一次工具去生成图片
        - 输出报告面向普通用户，sql语句只是你的工具功能，禁止报告中出现sql语句
        - 输出数据报告用Markdown格式，要图文并茂。
        - 不能无中生有乱造数据和图片。
        """

    ),
    tools=[run_sql_queries, get_excel_info_tool, generate_bar_chart, generate_pie_chart],
    memory=chat_memory,
    verbose=True
)


async def analyze_question(question):
    global is_uploaded
    if not is_uploaded:
        gr.Warning("请先上传Excel文件")
        return "请先上传Excel文件"
    agent_workflow = AgentWorkflow(
        agents=[analyze_agent],
        root_agent=analyze_agent.name,
    )

    handler = agent_workflow.run(
        user_msg=question,
        memory=chat_memory
    )
    current_agent = None
    current_tool_calls = ""
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
    return final_output


def load_excel(file):
    global is_uploaded
    # 清除之前加载的数据
    # 清除 sheets_db
    # clear_sheets_db()
    # 清除动态创建的全局变量
    table_names = list(get_all_table_names(get_sheets_db()))
    print(table_names)
    for name in table_names:
        if name in get_sheets_db():
            try:
                del get_global()[name]
            except KeyError:
                pass
    clear_sheets_db()

    # 读取 Excel 文件
    sheets_db = pd.read_excel(file.name, sheet_name=None)
    set_sheets_db(sheets_db)
    print(f"成功加载 {len(sheets_db)} 个工作表: {', '.join(get_all_table_names(sheets_db))}")

    # 将字典中的 DataFrame 分配变量名（例如表名）
    for sheet_name, df in sheets_db.items():
        get_global()[sheet_name] = df  # 动态创建变量（如 orders、customers）
        if not is_regular_table(df):
            print(f"表 {sheet_name} 不是正规表格，拒绝加载。")
            gr.Warning(f"表 {sheet_name} 不是正规表格，拒绝加载。")
            return f"表 {sheet_name} 不是正规表格，拒绝加载。"
    info_str = get_excel_info_tool()
    # 打印 DataFrame 的信息和前几行数据
    print(info_str)
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

    file_input.upload(load_excel, inputs=file_input, outputs=load_output)
    # Modify the submit call to add loading state control
    question_input.submit(
        fn=analyze_question,
        inputs=question_input,
        outputs=answer_output,
        queue=True
    )

if __name__ == "__main__":
    excel_view.launch()
