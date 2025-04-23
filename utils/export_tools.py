"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/15 10:43
*  @FileName:   pdf_tools.py
**************************************
"""
import gradio as gr
from fpdf import FPDF
from mistletoe import markdown


def export_to_pdf(text):
    if not text.strip():  # 判断文本是否为空
        gr.Warning("当前分析结果为空，不能导出")
        return None
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('ArialUnicode', '', './fonts/arialuni.ttf', uni=True)
    pdf.set_font('ArialUnicode', size=12)
    # pdf.add_font('fireflysung', '', './fonts/fireflysung.ttf', uni=True)
    # pdf.set_font('fireflysung', '', 14)
    # pdf.multi_cell(0, 10, txt=text)
    pdf_path = "../output/analysis_result.pdf"
    html = markdown(text)
    # md = (
    #     MarkdownIt("commonmark", {"breaks": True, "html": True})
    #     .enable("strikethrough")
    #     .enable("table")
    # )
    # pdf.write(text=html)
    # html = md.render(text)
    print("----------------------------------")
    print(html)
    pdf.write_html(html)
    pdf.output(pdf_path)
    return pdf_path


# 导出成markdown
async def export_to_markdown(text):
    if not text.strip():  # 判断文本是否为空
        gr.Warning("当前分析结果为空，不能导出")
        return None
    md_path = "output/analysis_result.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(text)
    # 关闭文件
    f.close()
    return md_path
