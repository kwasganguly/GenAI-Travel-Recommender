## Use httpx-0.27.0
## Use OpenAI-1.30.5

import os
import streamlit as st
from llama_index.llms.openai import OpenAI as LlamaOpenAI
from llama_index.core import Settings, VectorStoreIndex, SimpleDirectoryReader

# Set your OpenAI API key
if "OPENAI_API_KEY" in st.secrets:
    my_api_key = st.secrets["OPENAI_API_KEY"]
else:
    my_api_key = st.sidebar.text_input(
        label = "#### Set your OpenAI API key here 👇",
        placeholder = "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        type = "password")

# Set your data directory path
if "DATA_DIRECTORY_PATH" in st.secrets:
    my_directory_path = st.secrets["DATA_DIRECTORY_PATH"]
else:
    my_directory_path = st.sidebar.text_input(
        label = "#### Set your data directory path here 👇",
        placeholder = "C:\\path\\to\\your\\data\\directory",
        type = "default")

# App title
st.title("Travel Recommender")

# Set OpenAI model to the Streamlit session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Set messages to the Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Iterate over the messages in the Streamlit session state and display them
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Add user input and response to the Streamlit session state
if prompt := st.chat_input("Hi! What's up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Set up the LlamaOpenAI model with specified settings
    Settings.llm = LlamaOpenAI(
        system_prompt = "You are a helpful travel assistant. When asked a question, answer from the data directory. \
            If you don't know the answer, say 'Oh, snap! It seems I've hit a road bump in my knowledge highway. \
            No worries, though! How about we detour to another fantastic journey waiting for you in the directory?'. \
            If you know the answer, please provide trip information not in a list but in text.",
        model = st.session_state["openai_model"],
        openai_api_key = my_api_key,
        max_tokens = 250
    )

    if os.path.isdir(my_directory_path):
        # Load documents from the specified directory
        documents = SimpleDirectoryReader(my_directory_path).load_data()

        # Create a VectorStoreIndex from the loaded documents
        index = VectorStoreIndex.from_documents(documents)

        with st.chat_message("assistant"):
            # Set up a query engine for the index and perform a streaming query
            query_engine = index.as_query_engine(streaming = True)
            streaming_response = query_engine.query(prompt)
            response_gen = streaming_response.response_gen

            # Write the streaming response to the Streamlit app
            response = st.write_stream(response_gen)
        st.session_state.messages.append({"role": "assistant", "content": response})

    else:
        st.error(f"Not a valid directory: {my_directory_path}")