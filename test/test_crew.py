"""
**************************************
*  @Author  ：   oujiangping
*  @Time    ：   2025/4/19 11:49
*  @FileName:   test_crew.py
**************************************
"""
import os

from crewai import LLM

from crew.table_crew import TableCrew

# 假设之前有未展示的代码，这里用省略号表示
# ... existing code ...
OPENAI_API_BASE = os.environ["OPENAI_API_BASE"]
OPENAI_MODEL_NAME = os.environ["OPENAI_MODEL_NAME"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
# ... existing code ...

llm = LLM(
    model=OPENAI_MODEL_NAME,
    base_url=OPENAI_API_BASE,
    api_key=OPENAI_API_KEY,
    temperature=0.7,  # Higher for more creative outputs
    timeout=120,  # Seconds to wait for response
    max_tokens=4000,  # Maximum length of response
    top_p=0.9,  # Nucleus sampling parameter
    frequency_penalty=0.1,  # Reduce repetition
    presence_penalty=0.1,  # Encourage topic diversity
    seed=42  # For reproducible results
)


if __name__ == '__main__':
    file_path = "data/学生成绩表.xlsx"
    inputs = {
        "file_path": file_path,
    }
    table_crew = TableCrew(file_path)
    result = table_crew.crew().kickoff(inputs=inputs)
    print(result)
