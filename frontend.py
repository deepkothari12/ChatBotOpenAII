import streamlit as st
from backend_code.backend    import thread_id , workflow
from langchain_core.messages import HumanMessage
from backend_code.cmdlogic   import handle_local_commands

st.markdown(
    """
    <style>
    .custom-footer {
        text-align: center;
        font-size: 14px;
        color: #999;z
        margin-top: 10px;
        margin-bottom: -10px; /* Slightly push toward the chat box */
    }
    </style>
    <div class="custom-footer">
        ☻ To enable Agent Mode, type <b>Nexi Agent On</b>.
    </div>
    """,
    unsafe_allow_html=True
)

# Store message history
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Store Agent Mode state
if 'agent_mode' not in st.session_state:
    st.session_state['agent_mode'] = False

# Display chat history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_input = st.chat_input('Type here')

agent_cmd = {"agent_mode_on": [
        "nexi agent on",
        "nexi agent on."
        "agent mode on",
        "agent On"
        "turn agent mode on",
        "enable agent mode",
        "activate agent mode",
        "start agent mode",
        "agent"
    ],
    "agent_mode_off": [
        "nexi agent off",
        "nexi agent off."
        "agent mode off",
        "agent On"
        "turn agent mode off",
        "disable agent mode",
        "deactivate agent mode",
        "stop agent mode"
        "no agent"
    ]}

if user_input:
    user_text = user_input.strip().lower()
    # print(user_text)

    # Add user's message to history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    
    if user_text in agent_cmd['agent_mode_on'] : # == "agent mode on":
        st.session_state['agent_mode'] = True
        ai_message = "✅ Agent Mode is now **ON**. I can execute commands."
        st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
        with st.chat_message('assistant'):
            st.markdown(ai_message)
        st.stop()

    elif user_text in agent_cmd['agent_mode_off']:
        st.session_state['agent_mode'] = False
        ai_message = "❌ Agent Mode is now **OFF**. I'll only chat."
        st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
        with st.chat_message('assistant'):
            st.markdown(ai_message)
        st.stop()

    # --- Handle commands if Agent Mode is ON ---
    if st.session_state['agent_mode'] and handle_local_commands(user_text):
        ai_message = f"🛠 Executed command: {user_input}"
        st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
        with st.chat_message('assistant'):
            st.markdown(ai_message)
        st.stop()

    # # --- Normal AI response ---
    # config = {"configurable": {"thread_id": thread_id}}
    # try:
    #     response = workflow.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    #     # print(response)
    # except:
    #     raise Exception("No Connections Or API error")
    # # ##for the streaming
    # ai_message = response['messages'][-1].content

    # st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})

    # with st.chat_message('assistant'):
    #     st.markdown(ai_message)

    ##streamiing 
    # --- Normal AI response (with streaming) ---
    config = {"configurable": {"thread_id": thread_id}}

    try: 
        # Stream response instead of full invoke
        response_stream = workflow.stream({'messages': [HumanMessage(content=user_input)]}, config=config)
        # print(response_stream)
    except:
        raise Exception("No Connections Or API error")

    # Placeholder in chat to update incrementally
    with st.chat_message('assistant'):
        message_placeholder = st.empty()
        full_response = ""

        # Stream tokens as they arrive
        for event in response_stream:
            # print("-->" , event.values())
            for value in event.values():
                # print("->",value)  
                if hasattr(value, "content"):
                    token = value.content
                    full_response += token
                    message_placeholder.markdown(full_response + "▌")

              
                elif isinstance(value, dict):
                    if "messages" in value:
                        for msg in value["messages"]:
                            if hasattr(msg, "content"):
                                token = msg.content
                                full_response += token
                                # print(full_response)
                                message_placeholder.markdown(full_response + "▌")
                # Final update (remove typing cursor ▌)
                # message_placeholder.markdown(full_response)

    # Save to session history
    st.session_state['message_history'].append({'role': 'assistant', 'content': full_response})

    




    