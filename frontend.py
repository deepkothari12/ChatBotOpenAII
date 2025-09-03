import streamlit as st
from backend_code.backend import workflow, find_all_thread, gpt_models_streaming
from langchain_core.messages import HumanMessage, AIMessage
import uuid

############### Utility Functions ###############
def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

    # # Initialize empty thread in DB so it appears in history
    # workflow.invoke(
    # {"messages": [HumanMessage(content=user_input), AIMessage(content=full_response)]},
    # config={"configurable": {"thread_id": st.session_state['thread_id']}}
    # )

def chat_within_thread_id(thread_id):
    """Get messages stored in DB for a given thread"""
    state = workflow.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages")

def load_thread_messages(thread_id):
    """Format messages from DB for Streamlit display"""
    load_chat = chat_within_thread_id(thread_id)
    temp_messages = []
    if load_chat:
        for messag in load_chat:
            if isinstance(messag, HumanMessage):
                role = "user"
            elif isinstance(messag, AIMessage):
                role = "assistant"
            else:
                continue
            temp_messages.append({"role": role, "content": messag.content})
    return temp_messages

######################################## Session State ########################################
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = find_all_thread()

add_thread(st.session_state["thread_id"])

if "agent_mode" not in st.session_state:
    st.session_state["agent_mode"] = False

######################################## Side-Bar ########################################
st.sidebar.title("Lang Graph ChatBot")
if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("Your History")
for thread_id in st.session_state["chat_threads"]:
    load_chat = chat_within_thread_id(thread_id)
    display_title = load_chat[0].content[:20] if load_chat else "empty chat"

    if st.sidebar.button(display_title, key=f"btn-{thread_id}"):
        st.session_state["thread_id"] = thread_id
        st.session_state["message_history"] = load_thread_messages(thread_id)

######################################## Display Chat ########################################
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Type here")

######################################## Streaming Response ########################################
if user_input:
    # Add user input to history
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Prepare messages for backend
    api_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state["message_history"]]

    # Stream assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in gpt_models_streaming(api_messages):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    # Save assistant response in session + DB
    st.session_state["message_history"].append({"role": "assistant", "content": full_response})

    workflow.invoke(
        {"messages": [
            HumanMessage(content=user_input),
            AIMessage(content=full_response)
        ]},
        config={"configurable": {"thread_id": st.session_state['thread_id']}}
    )
