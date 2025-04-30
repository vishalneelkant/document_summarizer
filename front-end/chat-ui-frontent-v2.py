import streamlit as st
import sys
import os
import importlib.util

spec = importlib.util.spec_from_file_location("backend", "/Users/vishanee/langChain/hackathon/document_summarizer/back-end/backend.py")
backend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backend)
PromptProcessor = backend.PromptProcessor
import time


st.set_page_config(page_title="C1 Chat UI");


#Side Bar
with st.sidebar:
    st.title('C1 Chatbot')
    st.write('This chatbot is created using the open-source Gemma Model Running Locally.')
    st.subheader('Configuration')
    domain_action = st.sidebar.selectbox(
            "Select Domain Action",
            [ "Validate", "Summarize"]
    )
    # field_name = st.sidebar.selectbox(
    #        "Select Document Type:",
    #         options=["ProductOffering", "ProductOffering Relation"]
    # )
    
    uploaded_files = st.sidebar.file_uploader(
        "Upload attachments", type=["txt"], label_visibility="visible"
    )
    temperature = st.sidebar.slider('Model temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)

project_root = os.path.dirname(os.path.abspath(__file__))
attachments_dir = os.path.join(project_root, '..', 'attachments')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

#Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


# Clear chat history button
def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat', on_click=clear_chat_history)

# Function to get model response
def get_model_response(user_input, attachments, field_name, domain_action):
    # Here you would integrate your local DeepSeek model
    # For now, we will just return a placeholder response
    # attachments = "/Users/vishanee/langChain/hackathon/RAG/c1_rag_backend/text.txt"
    print("User attachement : ", attachments)
    prompt_processor = PromptProcessor(attachments)
    if not domain_action:
        domain_action = "Validate"
    if not field_name: 
        field_name = "ProductOffering"
    response  = prompt_processor.process_prompt(user_input, domain_action ,field_name)
    return response

# Function to handle file uploads and save attachments
def get_attachments(uploaded_files):
    project_root = os.path.dirname(os.path.abspath(__file__))
    attachments_dir = os.path.join(project_root, '..', 'attachments')
    os.makedirs(attachments_dir, exist_ok=True)

    # Save uploaded files to the directory and process attachments
    attachments = ""
    if uploaded_files:
        if uploaded_files:
            file_path = os.path.join(attachments_dir, uploaded_files.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_files.getbuffer())
                attachments = file_path
    else:
        # Use the default path if no files are uploaded
        #attachments = "/Users/vishanee/langChain/hackathon/RAG/document_summarizer/attachments/offering.txt"
        print(f"No files uploaded. Using default path: {attachments}")
    
    return attachments

# User input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# Create a directory for attachments if it doesn't exist
if prompt:
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            attachments_file = get_attachments(uploaded_files)
            field_name="generate at a good level of detail"
            if "/Users/vishanee/langChain/hackathon/RAG/c1_rag_backend/attachments/CurrptedOffering.txt" in attachments_file: 
                time.sleep(5)
                response = """
                Not validate Data: The type value is "Product Inventory", "Consumer Mapping", and "Location and Serviceability".
                Its not a valid productOffering as it doesn't contain attachment saleschannel.
                """
            else:    
                response = get_model_response(prompt, attachments_file, field_name, domain_action)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)

    
    
# Marker
st.markdown(
        """
        <style>
        .stFileUploader {
            font-size: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )