from autogen import config_list_from_json
import autogen

# 配置 api key

config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")
llm_config = {
    "config_list": config_list, 
    "seed": 42, 
    "temperature": 0.2,
}

# 创建 user proxy agent, coder, product manager  三个不同的角色
user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin who will give the idea and run the code provided by Coder.",
    code_execution_config={
        "last_n_messages": 3,  #最多接收的响应的数量
        "work_dir": "groupchat",
        "use_docker": False
    }, 
    human_input_mode="ALWAYS", #注意这个 mode 的选择
    
)

coder = autogen.AssistantAgent(
    name="Coder",
    llm_config=llm_config,
)

pm = autogen.AssistantAgent(
    name="product_manager",
    system_message="You will help break down the initial idea into a well scoped requirement for the coder; Do not involve in future conversations or error fixing",
    llm_config=llm_config,
)

# 创建 组 groupchat
groupchat = autogen.GroupChat(
    agents=[user_proxy, coder, pm], 
    messages=[]
)
manager = autogen.GroupChatManager(
    groupchat=groupchat, 
    llm_config=llm_config,
    system_message="Manage the conversation between agents. Ensure the coder provides runnable code and the user proxy executes it."
)

# 初始化 开始干活
# user_proxy.initiate_chat(
#     manager, 
#     message="Build a classic & basic pong game with 2 players in python"
# )
try:
    user_proxy.initiate_chat(
        manager, 
        message="Build a classic & basic pong game with 2 players in python using pygame"
    )
except Exception as e:
    print(f"对话过程中发生错误: {e}")
    print("尝试简化对话...")
    
    # 如果组聊失败，尝试直接对话
    user_proxy.initiate_chat(
        coder,
        message="Build a classic & basic pong game with 2 players in python using pygame. Provide complete runnable code."
    )