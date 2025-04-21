import os

import openai
from llama_index.core.workflow import Context

ANALYZE_LLM_MODEL_NAME = os.getenv("ANALYZE_LLM_MODEL_NAME")


async def analyze_table(ctx: Context, user_question: str) -> str:
    """
    表格数据分析工具
    输入数据：
    :param user_question: 结合历史聊天记录总结出用户当前的实际问题
    :return: 分析结果
    """
    excel_table = await ctx.get("table")
    # 修正：使用 len() 函数获取字符串长度
    if len(excel_table.get_markdown()) > 10000:
        return "非正规表格数据过大，本工具不支持分析，请重新上传表格"
    return analyze_with_llm(excel_table.get_markdown(), user_question)


# 利用openai的接口去分析表格数据
def analyze_with_llm(table_data: str, user_question: str) -> str:
    llm = openai.OpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = llm.chat.completions.create(
        model=ANALYZE_LLM_MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的表格统计分析建议生成助手，也是数据洞察助手，擅长输出数据报告，分析结果可以使用表格或者别的形式返回。"
            },
            {
                "role": "user",
                "content": f"""
                ## 注意事项
                - 注意即使用户问题中包含要图片，你也没有生成图片和图表的权限，你输出的文字报告我会再拿其它工具去生成图片（包括图片链接），所以你不能生成图片，而是报告中的数据尽量给我一些易于去生成图表的数据即可。
                
                ## 要求
                - 充分考虑文件布局，与实际表格内容
                - 按照markdown表格格式去理解表格数据
                - 要有好的记忆能力
                - 不要胡编乱造
                
                ## 表格数据如下
                {table_data}
                ## 用户问题如下
                {user_question}
                """
            }
        ]
    )
    return response.choices[0].message.content
