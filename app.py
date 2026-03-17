# app.py
import streamlit as st
from chatbot import load_models_and_kb, retrieve_relevant_chunks, generate_response

# --- Page Configuration ---
st.set_page_config(
    page_title="Zomato Restaurant Chatbot",
    page_icon="🍽️",
    layout="wide"
)

# --- Load Models and KB ---
# Use st.cache_resource to load models only once
@st.cache_resource
def load_resources():
    """Loads all necessary models and data. Cached by Streamlit."""
    if not load_models_and_kb():
        st.error("Failed to load necessary models or knowledge base. Please check logs.")
        return False
    return True

# --- Initialize ---
models_loaded = load_resources()

# --- UI Elements ---
st.title("🍽️ Zomato Restaurant Chatbot")
st.caption("Ask me questions about restaurants based on our (simulated) scraped data!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if prompt := st.chat_input("Ask something about restaurants... (e.g., 'Any vegetarian starters?')"):
    if not models_loaded:
        st.error("Chatbot is not available due to loading errors.")
    else:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        with st.spinner("Thinking..."):
            try:
                # 1. Retrieve relevant context
                relevant_chunks = retrieve_relevant_chunks(prompt)

                # 2. Generate response using RAG
                response = generate_response(prompt, relevant_chunks)

            except Exception as e:
                response = f"An error occurred: {e}"
                st.error(response) # Show error in UI as well

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

# Add a sidebar for potential future controls or info
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot uses a Retrieval Augmented Generation (RAG) approach
    to answer questions about restaurants.

    **Data:** Based on *simulated* scraped data.
    **Models:** Uses Hugging Face's Sentence Transformers for retrieval
    and Flan-T5 for generation.
    """)
    if not models_loaded:
        st.warning("Models failed to load. Chatbot may not function correctly.")

