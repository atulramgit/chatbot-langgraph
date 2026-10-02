import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage

CONFIG = {"configurable" : {"thread_id" : "thread-1"}}

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

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
    
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])
        

user_input = st.chat_input('Type here')

if user_input:
    
    st.session_state['message_history'].append({"role" : "user", "content" : user_input})
    with st.chat_message('user'):
        st.text(user_input)
        
        
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