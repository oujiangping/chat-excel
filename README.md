# Chat-Excel Project

## Project Introduction
The `chat-excel` repository is a Python-based project utilizing LLamaIndex, designed to process Excel data with the help of large language models. The project can read Excel files and load worksheets as `DataFrame`. Users can input questions, and the project uses an agent to generate SQL queries to perform statistical analysis on Excel data.

[中文 Chinese README](README.zh.md)

## Main Features
- Read Excel files and load worksheet data.
- Analyze user questions using `FunctionAgent` and generate SQL queries.
- Execute SQL queries in batch and return analysis results.
- Validate table compliance to avoid irregular format data affecting the analysis.
- Support multi-worksheet queries.
- Provide a Gradio interface for user interaction.
- Support Markdown export, which can be opened and converted with Markdown editors.
- Analyze non-standard tables with merged cells.

## Output Examples
Screenshots:
![gradio.png](asserts/gradio.png)

![img.png](asserts/img.png)

## Core Code
### Main Program
`main.py`: The main program responsible for reading files and handling user queries.

### Utility Functions
Defines multiple utility functions, such as getting sheet names, checking table compliance, executing SQL queries, etc.

### Agent Configuration
Configures the `FunctionAgent` to handle table-related queries.

## Installation and Usage
### Install Dependencies
```bash
pip install -r requirements.txt
```
Command to generate `requirements.txt`:
```bash
pipreqs ./ --encoding=utf8 --force
```

### Set Environment Variables
Create a `.env` file and set the following environment variables:
```bash
OPENAI_API_KEY=your_key
OPENAI_API_BASE=api_address
OPENAI_MODEL_NAME=primary_model
ANALYZE_LLM_MODEL_NAME=table_analysis_model (usually deepseek-v3)
```

### Run the Project
```bash
python main.py
```

## Notes
- Ensure the Excel file path is correct.
- Ensure the file is compliant to avoid data format errors; merged cells are not allowed.
- Ensure environment variables are set correctly.

## TODO
- Enhance the user interface experience.
- Support more features.