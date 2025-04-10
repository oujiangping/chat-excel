"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/11 13:58
*  @FileName:   quickchart.py
**************************************
"""
from typing import List, Dict
from quickchart import QuickChart


# 生成图片的公共函数
def generate_chart(data) -> str:
    qc = QuickChart()
    qc.width = 500
    qc.height = 300
    qc.device_pixel_ratio = 2.0
    qc.config = data
    return qc.get_url()


# 条形图工具
def generate_bar_chart(labels: List[str], datasets: List[Dict[str, object]]) -> str:
    """
    生成条形图工具
    输入数据：
    :param labels: 数组
    :param datasets: 数组
    :return: url

    输入数据样例:
    labels代表x轴，datasets代表y轴
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      { label: 'Dogs', data: [50, 60, 70, 180, 190] },
      { label: 'Cats', data: [100, 200, 300, 400, 500] },
    ],
    """
    char_data = {
        "type": "bar",
        "data": {
            "labels": labels,
            "datasets": datasets
        }
    }
    return generate_chart(char_data)


"""
{
  type: 'pie',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [{
      data: [50, 60, 70, 180, 190]
    }]
  }
}
"""


# 饼图工具
def generate_pie_chart(labels: List[str], datasets: List[Dict[str, object]]) -> str:
    """
    生成饼图工具（只支持一组标签和一组对应的数据）
    输入数据：
    :param labels: 数组
    :param datasets: 数组
    :return: url
    输入数据样例:
    labels代表数据标签，datasets代表数据(饼图一般只有一个数据集)
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      { data: [50, 60, 70, 180, 190] },
    ],
    """
    char_data = {
        "type": "pie",
        "data": {
            "labels": labels,
            "datasets": datasets
        }
    }
    return generate_chart(char_data)
