import os

from langchain.agents import initialize_agent
from langchain.llms.ai21 import AI21
from langchain.memory import ConversationBufferWindowMemory
import dotenv
from langchain_core.messages import SystemMessage
import os
from datetime import datetime

import dotenv
from langchain.agents import Tool
from langchain.chains import LLMMathChain
from langchain.llms.ai21 import AI21
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain_experimental.utilities import PythonREPL


dotenv.load_dotenv()
HUGGINGFACE_KEY = os.getenv("HUGGINGFACEHUB_API_TOKEN")
AI21_API_KEY = os.getenv("AI21_LLM_key")

PREFIX = """Answer the following questions as best you can only using the following tools:
 Calculator: Useful for when you need to answer questions about math and arithmetics.
 python_repl: Useful when you need to execute python commands.
 duckduckgo: Useful for when you need to search the internet for something another tool cannot find.
 Datetime:useful to return the current datetime 
 """
FORMAT_INSTRUCTIONS = """Use the following format:

 Question: the input question you must answer
 Thought: you should always think about what to do. Always use a tool
 Action: the action to take, should be one of [{tool_names}]
 Action Input: the input to the action
 Observation: the result of the action 
 ... (this Thought/Action/Action Input/Observation can repeat N time)
 Thought: I now know the final answer
 Final Answer: the final answer to the original input question

 If you can't find the answer, you will respond as follows: Final Answer: Sorry 😔, I don't know the answer. I will 
 do my best next time! 

 """
SUFFIX = """Begin! Remember to give the observation as a final answer:

 Question: {input}
 Thought:{agent_scratchpad}"""
sys_msg = """Assistant is a large language model trained by AI21 Studio.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing 
in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate 
human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide 
responses that are coherent and relevant to the topic at hand. 

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process 
and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a 
wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, 
allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics. 

Unfortunately, Assistant is very terrible at maths . When provided with any questions, no matter how simple, 
assistant always refers to it's trusty tools and absolutely does NOT try to answer questions by itself 

Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and 
information on a wide range of topics. Whether you need help with a specific question or just want to have a 
conversation about a particular topic, Assistant is here to assist. """

llm = AI21(ai21_api_key=AI21_API_KEY, temperature=0.3, verbose=False)
datetime_tool = Tool(
    name="Datetime",
    func=lambda x: datetime.now().isoformat(),
    description="Returns the current datetime",
)
tools = [datetime_tool]
llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=False)
tools.append(
    Tool.from_function(
        func=llm_math_chain.run,
        name="Calculator",
        description="Use this tool when you need to answer questions only about math and arithmetic",
    )
)

python_repl = PythonREPL()
tools.append(
    Tool.from_function(
        name="python_repl",
        description="Use A Python shell. Use this to execute python commands. Input should be a valid python command. "
                    "If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl.run,
    )
)

duck = DuckDuckGoSearchAPIWrapper(region="en-us", max_results=10)
tools.append(
    Tool.from_function(
        name="duckduckgo",
        description="Useful for finding information about a specific topic. Useful for when you need to search the "
                    "internet for something another tool cannot find.",
        func=duck.run,

    )
)

system_message = SystemMessage(
    content=sys_msg
)
agent_kwargs = {
    "system_message ": system_message
}
memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    return_messages=True,
    verbose=True,
)

agent = initialize_agent(
    llm=llm,
    agent='conversational-react-description',
    prefix=PREFIX,
    suffix=SUFFIX,
    format_instructions=FORMAT_INSTRUCTIONS,
    tools=tools,
    max_iteration=10,
    handle_parsing_errors=True,
    verbose=True,
    agent_kwargs=agent_kwargs,
    memory=memory,
    early_stopping_method="generate",
)
