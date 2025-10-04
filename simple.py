import autogen
from autogen import AssistantAgent, UserProxyAgent, config_list_from_json


# config_list = [
#     {
#         "model": "deepseek-chat",  # 或者 "deepseek-coder"
#         "api_key": "sk-CkGPdUD1kiyYZycrVJLjMIqsAO6Kyp0ELOax8MP5zyP5RyOB",  # 替换为你的API密钥
#         "base_url": "https://globalai.vip",  # DeepSeek API地址
#     }
# ]

# 加载配置文件（正确提取 config_list）
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")


# 创建 AssistantAgent（llm_config 只保留 config_list，不单独指定 api_type）
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "config_list": config_list, 
        "temperature": 0.2
    }
)

# 创建 UserProxyAgent
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={
        "work_dir": "sources_simple",  # 存放代码的目录
        "use_docker": False  # 本地测试关闭 Docker
    },
    human_input_mode="ALWAYS",  # 不需要人工输入
    max_consecutive_auto_reply=3    # 自动回复次数
)

# 启动任务
# 启动任务
user_proxy.initiate_chat(
    assistant,# 这里指定对话的AssistantAgent对象
    message="Plot a chart of NVDA and TESLA stock price change YTD. "
            "Use yfinance to get stock data, and matplotlib to plot the chart. "
            "Save the chart as 'stock_chart.png' in the '/data/icy/code/Microsoft_AutoGen_Tutorial/sources_simple/pics' directory."
)