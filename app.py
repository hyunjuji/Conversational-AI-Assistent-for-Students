import datetime as dt
import inspect
import json
import os
import sys
from typing import Optional

from dotenv import load_dotenv
import gradio as gr
from duckduckgo_search import DDGS
from openai import AzureOpenAI
from pydantic import BaseModel


from src.gt_tools import gt_tools, gt_tools_dict
from src.program_functions import gtProgramManager
from src.calendar_functions import gtCalendarManager
from src.db_functions import query_university_db, get_db_schema

calendar_manager = gtCalendarManager()
program_manager = gtProgramManager()


load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"), 
    api_version="2024-12-01-preview", 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

class Agent(BaseModel):
    name: str = "Agent"
    model: str = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    instructions: str = "You are a helpful Georgia Tech student assistant."
    tools: list = []
    color: str = "\033[0m"  #default color

class Response(BaseModel):
    agent: Optional[Agent]
    messages: list

def function_to_schema(func) -> dict:
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try: 
        signature = inspect.signature(func)
    except Exception as e:
        raise ValueError(f"Failed to get signature for function {func.__name__}: {str(e)}")
    
    parameters = {}
    for param in signature.parameters.values():
        try: 
            param_type = type_map.get(param.annotation, "string")
        except Exception as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": (func.__doc__ or "").strip(),
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            }
        }
    }

def get_or_create_tool_schema(tool):
    tool_name = tool.__name__

    if tool_name in gt_tools_dict:
        return gt_tools_dict[tool_name]
    else:
        new_schema = function_to_schema(tool)
        gt_tools.append(new_schema)
        gt_tools_dict[tool_name] = new_schema
        return new_schema

def execute_tool_call(tool_call, tool_map, agent_name):

    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    return tool_map[name](**args)

def run_full_turn(agent, messages):

    current_agent = agent
    messages = messages.copy()
    num_init_messages = len(messages)


    while True:

        tool_schemas = [get_or_create_tool_schema(tool) for tool in current_agent.tools]
        tool_map = {tool.__name__: tool for tool in current_agent.tools}

        response = client.chat.completions.create(
            model = current_agent.model,
            messages = [{"role":"system", "content": current_agent.instructions}] + messages,
            tools = tool_schemas or None,
        )

        message = response.choices[0].message
        messages.append(message)

        print(message)

        if message.content:
            print(f"{current_agent.color}{current_agent.name}: {message.content}\033[0m")

        if not message.tool_calls:
            break

        for tool_call in message.tool_calls:
            result = execute_tool_call(tool_call, tool_map, current_agent.name)

            if type(result) == Agent:
                current_agent = result
                result = (
                    f"Transfered to {current_agent.name}."
                )

            result_message = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            }

            messages.append(result_message)

            print(messages)

    return Response(agent = current_agent, messages = messages[num_init_messages:])

def transfer_to_program_agent(**kwargs):
    """
    Call this agent if the user is asking about the program or courses.
    """
    return program_agent


def transfer_to_calendar_agent(**kwargs):
    """
    Call this agent if the user is asking about the calendar.
    """
    return calendar_agent


def get_dateandtime():
    now = dt.datetime.now().isoformat()
    return f"current date and time in isoformat: {now}"


def web_search(query: str, max_results: int = 5):
    """
    Fallback web search when database lacks information.

    Args:
        query (str): Search query string.
        max_results (int, optional): Number of search results to return. Defaults to 5.

    Returns:
        list[dict] | dict: On success, a list of results (title, href, snippet). On failure, a dict with error message.
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title"),
                    "href": r.get("href"),
                    "snippet": r.get("body")
                })
        return results
    except Exception as e:
        return {"error": str(e)}

def transfer_to_db_agent(**kwargs):
    """
    Call this agent if you need to query the university database to answer the user's question.
    """
    return db_agent


triage_agent = Agent(
    name = "Triage Agent",
    color = "\033[94m",  # 파란색
    # instructions = """
    # You are a helpful Georgia Tech student assistant.
    # Your job is to:
    # 1. FIRST, always get the user's information from the database using the transfer_to_db_agent tool
    # 2. After getting user information, transfer to the appropriate agent based on the user's inquiry:
    #    - For program/course related questions: transfer_to_program_agent
    #    - For calendar/schedule related questions: transfer_to_calendar_agent
    #    - For database queries: stay with db_agent
    # Always start by getting user information from the database before transferring to other agents.
    
    # RESPONSE STYLE: Be concise and direct. Keep responses brief and to the point.
    # """,
    instructions = """
    1. Important rules:
    - Be concise.
    2. Role:
    - You are a triage agent. Your job is to transfer to the appropriate agent based on the user's needs.
    - You can transfer to program_agent, calendar_agent.
    """,
    tools = [transfer_to_program_agent, transfer_to_calendar_agent, transfer_to_db_agent],
)


def transfer_to_triage_agent(**kwargs):
    """
    Call back to the triage agent if the user's question requires the other agent's help to answer.
    """
    return triage_agent


program_agent = Agent(
    name = "Program Agent",
    color = "\033[95m",  # 보라색
    # instructions = """
    # You are the Program Agent, one of the Georgia Tech student assistants.
    # Your responsibility is to help the user with their program and course related questions.
    
    # IMPORTANT: Check the conversation history first. If user information has already been retrieved by a previous agent, use that information directly.
    # Only transfer to db_agent if user information is completely missing from the conversation.
    
    # CRITICAL RULES FOR COURSE RECOMMENDATIONS:
    # 1. ALWAYS check what semester the user is asking about using get_dateandtime() first but do not use it again if you or another agent has already used it and you have the information.
    # 3. For course recommendations, ALWAYS verify that the courses are actually offered in the specified semester by querying the database
    # 4. Use query_university_db to check course offerings before making recommendations
    # 5. Only recommend courses that are confirmed to be offered in the requested semester
    # 6. CRITICAL: Before finalizing recommendations, check for time conflicts by querying the database for schedule information
    # 7. Use query_university_db to get schedule details (days, times) of recommended courses and check for overlaps
    # 8. If time conflicts are found, adjust recommendations to avoid scheduling conflicts
    
    # Use the following tools to help the user with their program and course related questions:
    # - get_dateandtime: Get current date/time to determine exact semester
    # - get_program_details: Get the details of the user's program
    # - get_semester_courses: Get the courses for the current semester
    # - query_university_db: Verify course offerings and check schedule conflicts in specific semesters
    
    # When making recommendations, consider:
    # - The user's current program (from database)
    # - Courses they have already taken (from database)
    # - Their GPA and academic standing (from database)
    # - Their semester enrollment (from database)
    # - ONLY courses that are actually offered in the requested semester (verified via database query)
    # - Schedule conflicts and time overlaps (verified via database query)
    
    # Provide personalized recommendations based on the user's academic history and program requirements.
    # You are the EXPERT for course recommendations and program advice.
    # DO NOT transfer to other agents unless absolutely necessary for additional information.
    # DO NOT refer to yourself in third person - you ARE the program agent, so provide recommendations directly.
    
    # RESPONSE STYLE: Be concise and focused. Provide clear, actionable recommendations without unnecessary explanations. Keep responses brief but informative.
    # IMPORTANT: DO NOT use phrases like 'hold on', 'please wait', 'while I check', or any language that suggests the user needs to wait. Execute actions immediately and provide results directly.
    # """,
    instructions = """
    1. Important rules:
    - Be concise.
    - If you need extra information, use transfer_to_db_agent to transfer to the db_agent.
    2. Role:
    - You are the program agent. Your job is to help the user with their program and course related questions.
    - You can transfer to db_agent, calendar_agent, triage_agent.
    3. Things to keep in mind based on frequent tasks:
    a. course recommendation
    - when user asks about course recommendation, recommend based on the user's program and user's course history.
    - Make available options with no schedule conflict. 
    """
    ,
    tools = [get_dateandtime, program_manager.get_program_details, transfer_to_triage_agent, transfer_to_db_agent,transfer_to_calendar_agent]
)



calendar_agent = Agent(
    name = "Calendar Agent",
    color = "\033[93m",  # yellow
    instructions = """
    You are one of the Georgia Tech student assistants.
    Your responsibility is to help the user with their calendar related questions.
    
    IMPORTANT: Check the conversation history first. If user information has already been retrieved by a previous agent, use that information directly.
    Only transfer to db_agent if user information is completely missing from the conversation.
    
    First, check the current date and time using the get_dateandtime tool but do not use it again if you or another agent has already used it and you have the information.
    Second, use the setup_credentials tool to set up the credentials for calendar.
    
    After that, you can use the following tools to help the user with their calendar related questions:
    - create_event: Create an event in the user's calendar
    - delete_event: Delete an event from the user's calendar
    - get_events: Get the events from the user's calendar
    
    When creating calendar events, consider the user's:
    - Course schedule (from database)
    - Program requirements
    - Academic commitments
    
    Provide personalized calendar management based on the user's academic profile.
    If you need to query the database for additional information, use transfer_to_db_agent.
    DO NOT transfer to other agents unless absolutely necessary for additional information.
    
    RESPONSE STYLE: Be concise and direct. Provide clear, actionable responses without unnecessary details.
    IMPORTANT: DO NOT use phrases like 'hold on', 'please wait', 'while I check', or any language that suggests the user needs to wait. Execute actions immediately and provide results directly.
    """,
    tools = [get_dateandtime, calendar_manager.setup_credentials, calendar_manager.create_event, calendar_manager.delete_event, calendar_manager.get_events, transfer_to_triage_agent, transfer_to_db_agent]
)

db_schema = get_db_schema()

db_agent = Agent(
    name = "Database Agent",
    color = "\033[92m",  # 초록색
    # instructions = (
    #     "You are a helpful Georgia Tech student assistant that can query the university database.\n"
    #     "You must use one of the transfer_to_triage_agent, transfer_to_program_agent, or transfer_to_calendar_agent tools to transfer to the appropriate agent.Do not just say you are transferring to the agent and not use the tool.\n"
    #     "Here is the database schema:\n"
    #     f"{db_schema}\n"
    #     "Your primary role is to retrieve user information and other data from the database.\n"
    #     "When the user asks a question, first identify what information is needed and generate an appropriate SQL query using the schema and call the 'query_university_db' tool.\n"
    #     "After retrieving the user information, provide a summary of the user's profile including:\n"
    #     "- Their program and academic standing\n"
    #     "- Courses they have taken\n"
    #     "- Any other relevant academic information\n"
    #     "IMPORTANT: You are ONLY responsible for retrieving and presenting data from the database.\n"
    #     "DO NOT make course recommendations or program advice - that is the program agent's job.\n"
    #     "CRITICAL: When the user asks for recommendations or advice, you MUST:\n"
    #     "1. FIRST check the current date/time using get_dateandtime() to understand the context but do not use it again if you or another agent has already used it and you have the information.\n"
    #     "2. If user mentions relative time (like 'next semester', 'this fall'), use get_dateandtime() to determine the exact semester\n"
    #     "3. Retrieve all necessary user information from the database using query_university_db\n"
    #     "4. Present the retrieved information clearly to the user, including the relevant semester context\n"
    #     "5. THEN transfer to program_agent using transfer_to_program_agent\n"
    #     "6. Do NOT transfer without first retrieving and presenting the user information\n"
    #     "If the user asks for calendar-related help, follow the same process but transfer to calendar_agent.\n"
    #     "Only answer direct database queries about data retrieval without transferring.\n"
    #     "RESPONSE STYLE: Be concise and focused. Present data clearly and efficiently without unnecessary explanations.\n"
    #     "IMPORTANT: DO NOT use phrases like 'hold on', 'please wait', 'while I retrieve', or any language that suggests the user needs to wait. Execute actions immediately and provide results directly."
    # ),
    instructions = """
    1. Important rules:
    - Be concise.
    - You should only use web_search tool if you cannot find the information using query_university_db.
    - Checking time conflicts for course recommendation is your job do not transfer to other agents for this.
    2. Role:
    - You are the database agent. Your job is to use the query_university_db tool to get the user's information and help other agents do their jobs based on these information.
    - Try using query_university_db first and use web_search tool if you cannot find the information, and be sure to inform the user that you used searched the web when you use web_search tool.
    - You can transfer to triage_agent, program_agent, calendar_agent after retrieving the user's information.
    - Try not to use query_university_db if you already have the information from the conversation history. (since it uses too much tokens.)
    - Transfer back to the agent that called you after retrieving the required information.
    """,
    tools = [get_dateandtime, query_university_db, get_db_schema, web_search, transfer_to_triage_agent, transfer_to_program_agent, transfer_to_calendar_agent]
)

async def main():
    agent = triage_agent
    messages = []

    while True:
        user = input("User: ")
        if user.lower() in ["quit", "exit", "bye"]:
            break
        
        messages.append({"role": "user", "content": user})
        response = run_full_turn(agent, messages)
        agent = response.agent
        messages.extend(response.messages)


chat_history = []

# def chat(user_message, history):
#     global chat_history
#     if user_message.lower() in ["quit", "exit", "bye"]:
#         sys.exit(0)
        
#     chat_history.append({"role": "user", "content": user_message})
#     response = run_full_turn(triage_agent, chat_history)
#     chat_history.extend(response.messages)
#     return response.messages[-1].content

def chat(user_message, history):
    global chat_history
    if user_message.lower() in ["quit", "exit", "bye"]:
        sys.exit(0)

    # append the user message to chat history
    chat_history.append({"role": "user", "content": user_message})

    # run the agent loop
    response = run_full_turn(triage_agent, chat_history)
    chat_history.extend(response.messages)

    # grab the last message and its role
    last_msg = response.messages[-1].content
    agent_name = response.agent.name

    bot_reply = f"**{agent_name}:** {last_msg}"

    return bot_reply

# Gradio chatting interface
gr.ChatInterface(fn=chat, title="GT Assistant Chatbot").launch()