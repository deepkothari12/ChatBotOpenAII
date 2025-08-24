from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver , InMemorySaver
from openai import OpenAI
import os
import requests
import json
from dotenv import load_dotenv
from backend_code.cmdlogic import handle_local_commands

load_dotenv()
HF_TOKEN = os.getenv('HF_TOKEN')


thread_id = "1"

# print(HF_TOKEN)
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def gpt_models(messages_list, prompt=None):
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key= HF_TOKEN,
    )
    
    api_messages = []
    
    if prompt:
        api_messages.append({"role": "system", "content": prompt})
    
    # Add all the conversation messages
    api_messages.extend(messages_list)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=api_messages,
        # stream=True,
        # stream_options=True
    )
    # print(completion)
    return completion.choices[0].message.content


def Chat_Node(state: ChatState):
    all_messages = state["messages"]
    # print(all_messages)
    formatted_messages = []
    for msg in all_messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        if isinstance(msg, BaseMessage):
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
    # print("--------->>>>" , formatted_messages)
    prompt = "You are a helpful AI assistant. Try to remember what the user said earlier and maintain context throughout the conversation."

    ai_response = gpt_models(formatted_messages, prompt)
    # print("----------->>>>>>>>",ai_response)
    return  {"messages": [AIMessage(content=ai_response)]}

graph = StateGraph(ChatState)
graph.add_node("Chat_Node", Chat_Node)
graph.add_edge(START, "Chat_Node")
graph.add_edge("Chat_Node", END)


checkpointer = InMemorySaver()  
workflow = graph.compile(checkpointer=checkpointer)


# thread_id = "11"
# print("Nexi: Hello! I'm your AI assistant. What's your name?")

# while True:
#     user_input = input("You: ")
#     if user_input.strip().lower() in ["tata", "bye", "exit", "stop" , 'by']:
#         print("Nexi: Bye! Nice chatting with you!")
#         break

#     config = {
#         "configurable": {
#             "thread_id": thread_id
#         }
#     }

#     response = workflow.invoke({
#         "messages": HumanMessage(content=user_input)
#     }, config=config)

#     print("Nexi:", response["messages"][-1].content)

# print(workflow.get_state(config=config).values['messages'])