from dotenv import load_dotenv, find_dotenv

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.format_scratchpad import format_to_openai_function_messages
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.agents import AgentExecutor
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import AIMessage, HumanMessage

from tools_definitions import symbolic_math
from langchain_experimental.tools import PythonREPLTool
from prompt_definitions import PROMPT1, PROMPT2

def load_environment():
    """Load environment variables from .env file."""
    load_dotenv(find_dotenv())

def define_tools():
    """Return list of tools. The tools are:
    PythonREPLTool(): used when we need to write and execute python code.
    """
    return [PythonREPLTool(), symbolic_math]

def define_llm_with_tools(tools):
    """Bind LLM with tools and return."""
    functions = [format_tool_to_openai_function(t) for t in tools]
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    return llm.bind(functions=functions)

def create_prompt(prompt):
    """Create and return a chat prompt template."""
    MEMORY_KEY = "chat_history"
    return ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder(variable_name=MEMORY_KEY),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

def create_agent(llm_with_tools, prompt):
    """
    Create and return the agent.

    The agent is constructed with a lambda dictionary that maps keys to functions:
    - 'input': Retrieves the 'input' from the lambda dictionary.
    - 'agent_scratchpad': Processes 'intermediate_steps' to format messages for the agent.
    - 'chat_history': Retrieves the 'chat_history' from the lambda dictionary.

    'intermediate_steps' represents previous agent actions and corresponding outputs,
    which are crucial for maintaining context in ongoing interactions.
    This data is passed to future iterations, allowing the agent to be aware of work already done.
    'intermediate_steps' is a list of tuples (AgentAction, Any), where 'observation' is of type Any
    for flexibility, often being a string.

    Args:
        llm_with_tools: The language model bound with functions (tools).
        prompt: The prompt template used by the agent.

    Returns:
        An agent that processes input, maintains a scratchpad, and keeps track of conversation history.
    """
    #TODO: not sure if this is the best way of creating an agent (specifically using OpenAIFunctionsAgentOutputParser),
    # eg it differs from https://python.langchain.com/docs/integrations/toolkits/python
    return (
        {
            "input": lambda x: x["input"],
            "agent_scratchpad": lambda x: format_to_openai_function_messages(x["intermediate_steps"]),
            "chat_history": lambda x: x["chat_history"],
        }
        | prompt
        | llm_with_tools
        | OpenAIFunctionsAgentOutputParser()
    )

def initialize_agent_executor(agent, tools, verbose):
    """Initialize and return the agent executor."""
    return AgentExecutor(agent=agent, tools=tools, verbose=verbose, handle_parsing_errors=True)

def run_chatbot(agent_executor):
    """Function to handle ongoing conversation using the agent with memory."""
    chat_history = []  # Initialize chat history

    while True:
        user_input = input("Human: ")

        # Exit condition
        if user_input.lower() in ['exit', 'quit', 'stop']:
            print("Exiting conversation.")
            break

        # Process the conversation using the agent executor
        result = agent_executor.invoke({"input": user_input, "chat_history": chat_history})

        # Update the chat history
        chat_history.extend([HumanMessage(content=user_input), AIMessage(content=result["output"])])

        # Print the chatbot's response
        print("Chatbot:", result["output"])

if __name__ == "__main__":

    prompt = PROMPT2

    load_environment()
    tools = define_tools()
    llm_with_tools = define_llm_with_tools(tools)
    prompt = create_prompt(prompt)
    agent = create_agent(llm_with_tools, prompt)
    agent_executor = initialize_agent_executor(agent, tools, verbose=False)
    run_chatbot(agent_executor)