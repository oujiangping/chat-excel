"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/22 14:07
*  @FileName:   view.py
**************************************
"""
import gradio as gr
import time
from concurrent.futures import ThreadPoolExecutor

# 定义全局加载弹框（带遮罩层）
loading_html = '''
<div id="loading-mask" style="display:block; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.5); z-index:10000;">
  <div style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center;">
    <div class="lds-ripple"><div></div><div></div></div>
    <p style="color:white; margin-top:10px; font-size:16px;">正在处理中，请勿执行其它操作</p>
  </div>
</div>

<style>
.lds-ripple {
  display: inline-block;
  position: relative;
  width: 64px;
  height: 64px;
}
.lds-ripple div {
  position: absolute;
  border: 4px solid #fff;
  opacity: 1;
  border-radius: 50%;
  animation: lds-ripple 1s cubic-bezier(0, 0.2, 0.8, 1) infinite;
}
.lds-ripple div:nth-child(2) {
  animation-delay: -0.5s;
}
@keyframes lds-ripple {
  0% { top: 28px; left: 28px; width: 0; height: 0; opacity: 1; }
  100% { top: -1px; left: -1px; width: 58px; height: 58px; opacity: 0; }
}
/* 移除 Gradio 框架的样式干扰 */
.wrap.center.full.svelte-ls20lj {
    border: none !important;
    outline: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
</style>
'''


def get_loading_view():
    return gr.HTML(loading_html, visible=False)
