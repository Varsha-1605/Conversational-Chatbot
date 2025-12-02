import streamlit as st
from langgraph_backend_tools import workflow, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid 

# ************************************ Utility Functions ****************************************---
# Function to generate a unique thread ID
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread-id'] = thread_id
    add_thread(st.session_state['thread-id'])
    st.session_state['message-history'] = []
    st.rerun()  # <-- forces immediate UI refresh

def add_thread(thread_id):
    if thread_id not in st.session_state['chat-thread']:
        st.session_state['chat-thread'].append(thread_id)

def load_conversation(thread_id):
    state = workflow.get_state(config={"configurable": {'thread_id': thread_id}})
    # Check if state has values and messages key
    if state.values and 'messages' in state.values:
        return state.values['messages']
    return []  # Return empty list if no messages found

# Define a generator function for streaming content
def stream_only_content():
    for chunk, metadata in workflow.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        ):
        if chunk.content:   # only print meaningful content
            yield chunk.content


# ************************************ Session History (INITIALIZE FIRST) ****************************************
if 'chat-thread' not in st.session_state:
    st.session_state['chat-thread'] = retrieve_all_threads()

if 'thread-id' not in st.session_state:
    st.session_state['thread-id'] = generate_thread_id()

if 'message-history' not in st.session_state:
    st.session_state['message-history'] = []

# Add current thread to the list
add_thread(st.session_state['thread-id'])

# Display existing messages
for message in st.session_state['message-history']:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ****************************************** sidebar UI ******************************************
st.sidebar.title("LangGraph Chatbot")
if st.sidebar.button("Add New"):
    reset_chat()

st.sidebar.header("My Conversations")
# st.sidebar.text(f"Current Thread ID:\n {st.session_state['thread-id']}")
for thread_id in st.session_state['chat-thread'][::-1]:
    if st.sidebar.button(f"Thread ID: {thread_id[:8]}..."):  # Show shortened ID for better UI
        st.session_state['thread-id'] = thread_id
        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                role = 'assistant'
            temp_messages.append({"role": role, "content": msg.content})

        st.session_state['message-history'] = temp_messages
        st.rerun()  # Refresh UI after loading conversation

# ************************************ Config *******************************************

CONFIG = {"configurable": {'thread_id': st.session_state['thread-id'] }}

# ************************************ Main Chat UI *******************************************
# Get user input
user_input = st.chat_input("Type here...")

if user_input:

    st.session_state['message-history'].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.markdown(user_input)


    with st.chat_message("assistant"):
        final_text = st.write_stream(stream_only_content())

    st.session_state['message-history'].append({"role": "assistant", "content": final_text})









