import asyncio
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage
from langgraph.graph import add_messages
from langgraph.checkpoint.memory import MemorySaver, InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver 
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
from fastapi import FastAPI
import json

load_dotenv()

if "HF_TOKEN" in st.secrets:
    HF_TOKEN = st.secrets["HF_TOKEN"]
else:
    HF_TOKEN = os.getenv("HF_TOKEN")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def gpt_models_streaming(messages_list, prompt=None):
    """Generator function for streaming responses"""
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
    
    api_messages = []
    
    if prompt:
        api_messages.append({"role": "system", "content": prompt})
    
    api_messages.extend(messages_list)
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=api_messages,
            stream=True,
        )
        
        # Collect all chunks for the complete response
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content  # Yield each chunk for real-time display
        
        return full_response
    
    except Exception as e:
        raise("No Data ")
def gpt_models_non_streaming(messages_list, prompt=None):
    """Non-streaming version for LangGraph compatibility"""
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=HF_TOKEN,
    )
    
    api_messages = []
    
    if prompt:
        api_messages.append({"role": "system", "content": prompt})
    
    api_messages.extend(messages_list)
    
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=api_messages,
            stream=False,  # No streaming for LangGraph
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        raise("Model is Sleeping")
    
def Chat_Node(state: ChatState):
    all_messages = state["messages"]
    
    formatted_messages = []
    for msg in all_messages:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        if isinstance(msg, BaseMessage):
            formatted_messages.append({
                "role": role,
                "content": msg.content
            })
    
    prompt = "You are a helpful AI assistant. Try to remember what the user said earlier and maintain context throughout the conversation."
    
    # Use non-streaming version for LangGraph
    ai_response = gpt_models_non_streaming(formatted_messages, prompt)
    
    return {"messages": [AIMessage(content=ai_response)]}

# Build the graph
graph = StateGraph(ChatState)
graph.add_node("Chat_Node", Chat_Node) 
graph.add_edge(START, "Chat_Node")
graph.add_edge("Chat_Node", END)

# Create Database
connections = sqlite3.connect(
    database="ChatBotData.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn=connections) 
workflow = graph.compile(checkpointer=checkpointer)

def find_all_thread():
    all_thread_id = set()
    for checkpoint in checkpointer.list(config=None):
        all_thread_id.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread_id)

# # Async streaming (more advanced)
# async def run_async_streaming_chat():
#     thread_id = "11"
#     print("Nexi: Hello! I'm your AI assistant. What's your name?")
    
#     conversation_history = []

#     while True:
#         user_input = input("You: ")
#         if user_input.strip().lower() in ["tata", "bye", "exit", "stop", 'by']:
#             print("Nexi: Bye! Nice chatting with you!")
#             break

#         conversation_history.append({"role": "user", "content": user_input})
        
#         print("Nexi: ", end="", flush=True)
        
#         # Simulate async streaming
#         full_response = ""
#         for chunk in gpt_models_streaming(conversation_history):
#             print(chunk, end="", flush=True)
#             full_response += chunk
#             await asyncio.sleep(0.01)  # Small delay for smooth streaming effect
        
#         print()
#         conversation_history.append({"role": "assistant", "content": full_response})

# asyncio.run(run_async_streaming_chat())