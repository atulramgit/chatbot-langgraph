import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

#**********************************Utility functions**************************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(config={"configurable" : {"thread_id" : thread_id}}).values['messages']

def parse_chunk_text(chunk) -> str:
    content = chunk.content
    
    # Standard string chunk
    if isinstance(content, str):
        return content
    
    # Block list chunk: [{"type": "text", "text": "..."}]
    if isinstance(content, list) and len(content) > 0:
        block = content[0]
        if isinstance(block, dict):
            return block.get("text", "")
        if isinstance(block, str):
            return block
            
    return ""

#***********************************Session setup****************************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
        
        
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()
    
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []
    
add_thread(st.session_state['thread_id'])
    
#**********************************Sidebar UI********************************************

st.sidebar.title('Langgraph Chatbot')

if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.header('My conversations')

for thread_id in st.session_state['chat_threads'][::-1]:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        
        temp_message= []
        
        for msg in messages:
            role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
            content = msg.content if isinstance(msg.content, str) else msg.content[0]['text']
            temp_message.append({"role": role, "content": content})

        st.session_state['message_history'] = temp_message

#***********************************main UI**********************************************

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        

user_input = st.chat_input('Type here')

if user_input:
    
    st.session_state['message_history'].append({"role" : "user", "content" : user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
    CONFIG = {"configurable" : {"thread_id" : st.session_state['thread_id']}}
    with st.chat_message('assistant'):
        
        def stream_generator():
            for chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        ):
                text = parse_chunk_text(chunk)
                if text:
                    yield text

        ai_response = st.write_stream(stream_generator())
        
    st.session_state['message_history'].append({"role" : 'assistant', 'content' : ai_response})