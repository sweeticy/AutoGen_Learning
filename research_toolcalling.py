import os
import autogen
from autogen import config_list_from_json, GroupChatManager, GroupChat, AssistantAgent, UserProxyAgent
import requests
from bs4 import BeautifulSoup
import json
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate
import openai
from dotenv import load_dotenv

# 获取各个 API Key
load_dotenv()
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST.json")

serper_api_key = os.getenv("SERPER_API_KEY")
browserless_api_key = os.getenv("BROWSERLESS_API_KEY")

# research 工具模块 - 修改为 Tool Calling 格式

def search(query):
    """Google search by Serper - 搜索工具"""
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

def scrape(url: str):
    """抓取网站内容 - 网页抓取工具"""
    print("Scraping website...")
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }
    data = {"url": url}
    data_json = json.dumps(data)
    post_url = f"https://chrome.browserless.io/content?token={browserless_api_key}"
    response = requests.post(post_url, headers=headers, data=data_json)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        print("CONTENT:", text)
        if len(text) > 8000:
            output = summary(text)
            return output
        else:
            return text
    else:
        print(f"HTTP request failed with status code {response.status_code}")
        return f"Error: Failed to scrape website, status code {response.status_code}"

def summary(content):
    """总结网站内容"""
    llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo-16k-0613")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"], chunk_size=10000, chunk_overlap=500)
    docs = text_splitter.create_documents([content])
    map_prompt = """
    Write a detailed summary of the following text for a research purpose:
    "{text}"
    SUMMARY:
    """
    map_prompt_template = PromptTemplate(
        template=map_prompt, input_variables=["text"])
    summary_chain = load_summarize_chain(
        llm=llm,
        chain_type='map_reduce',
        map_prompt=map_prompt_template,
        combine_prompt=map_prompt_template,
        verbose=True
    )
    output = summary_chain.run(input_documents=docs)
    return output

# 信息收集 - 修改为 Tool Calling
def research(query):
    """研究工具 - 收集信息"""
    
    # 定义 researcher agent 的 tools
    researcher_tools = [
        {
            "type": "function",    # 指定这是一个函数类型的工具
            "function": {
                "name": "search",
                "description": "Google search for relevant information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Google search query",
                        }
                    },
                    "required": ["query"],
                },
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "scrape",
                "description": "Scraping website content based on url",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string", 
                            "description": "Website url to scrape",
                        }
                    },
                    "required": ["url"],
                },
            }
        }
    ]

    # 使用 Tool Calling 配置
    llm_config_researcher = {
        "config_list": config_list,
        "tools": researcher_tools  # 使用 tools 而不是 functions
    }

    researcher = autogen.AssistantAgent(
        name="researcher",
        system_message="Research about a given query, collect as many information as possible, and generate detailed research results with loads of technique details with all reference links attached; Add TERMINATE to the end of the research report;",
        llm_config=llm_config_researcher,
    )

    user_proxy = autogen.UserProxyAgent(
        name="User_proxy",
        code_execution_config={"last_n_messages": 2, "work_dir": "sources_research2", "use_docker": False},
        is_termination_msg=lambda x: x.get("content", "") and x.get(
            "content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="TERMINATE",
        # 不再需要 function_map，AutoGen 会自动处理工具执行
    )

    # 注册工具到 user_proxy
    user_proxy.register_function(
        function_map={
            "search": search,
            "scrape": scrape,
        }
    )

    user_proxy.initiate_chat(researcher, message=query)

    user_proxy.stop_reply_at_receive(researcher)
    user_proxy.send(
        "Give me the research report that just generated again, return ONLY the report & reference links", researcher)

    return user_proxy.last_message()["content"]

# 编辑功能保持不变（这部分不需要工具调用）
def write_content(research_material, topic):
    editor = autogen.AssistantAgent(
        name="editor",
        system_message="You are a senior editor of an AI blogger, you will define the structure of a short blog post based on material provided by the researcher, and give it to the writer to write the blog post",
        llm_config={"config_list": config_list},
    )

    writer = autogen.AssistantAgent(
        name="writer", 
        system_message="You are a professional AI blogger who is writing a blog post about AI, you will write a short blog post based on the structured provided by the editor, and feedback from reviewer; After 2 rounds of content iteration, add TERMINATE to the end of the message",
        llm_config={"config_list": config_list},
    )

    reviewer = autogen.AssistantAgent(
        name="reviewer",
        system_message="You are a world class hash tech blog content critic, you will review & critic the written blog and provide feedback to writer.After 2 rounds of content iteration, add TERMINATE to the end of the message",
        llm_config={"config_list": config_list},
    )

    user_proxy = autogen.UserProxyAgent(
        name="admin",
        system_message="A human admin. Interact with editor to discuss the structure. Actual writing needs to be approved by this admin.",
        code_execution_config=False,
        is_termination_msg=lambda x: x.get("content", "") and x.get(
            "content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="TERMINATE",
    )

    groupchat = autogen.GroupChat(
        agents=[user_proxy, editor, writer, reviewer],
        messages=[],
        max_round=20)
    manager = autogen.GroupChatManager(groupchat=groupchat)

    user_proxy.initiate_chat(
        manager, message=f"Write a blog about {topic}, here are the material: {research_material}")

    user_proxy.stop_reply_at_receive(manager)
    user_proxy.send(
        "Give me the blog that just generated again, return ONLY the blog, and add TERMINATE in the end of the message", manager)

    return user_proxy.last_message()["content"]

# 出版 - 修改为 Tool Calling
# 定义 writing_assistant 的工具
writing_tools = [
    {
        "type": "function",     # 函数类型工具
        "function": {
            "name": "research",
            "description": "research about a given topic, return the research material including reference links", 
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The topic to be researched about",
                    }
                },
                "required": ["query"],
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_content", 
            "description": "Write content based on the given research material & topic",
            "parameters": {
                "type": "object", 
                "properties": {
                    "research_material": {
                        "type": "string",
                        "description": "research material of a given topic, including reference links when available",
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic of the content", 
                    }
                },
                "required": ["research_material", "topic"],
            },
        }
    }
]

llm_config_content_assistant = {
    "config_list": config_list,
    "tools": writing_tools  # 使用 tools 替代 functions--------------------------
}

writing_assistant = autogen.AssistantAgent(
    name="writing_assistant", 
    system_message="You are a writing assistant, you can use research function to collect latest information about a given topic, and then use write_content function to write a very well written content; Reply TERMINATE when your task is done",
    llm_config=llm_config_content_assistant,
)

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    human_input_mode="TERMINATE",
    # 不再需要 function_map
    code_execution_config={
        "work_dir": "sources_research2",
        "use_docker": False
    },
)

# 注册工具到 user_proxy
user_proxy.register_function(
    function_map={
        "research": research,
        "write_content": write_content,
    }
)

# 启动聊天
user_proxy.initiate_chat(
    writing_assistant, message="write a blog about autogen multi AI agent framework")