import streamlit as st
import requests
import logging
from src.core.config import settings

logger = logging.getLogger(__name__)

st.set_page_config(page_title="RepoSage", layout="wide")

st.title("RepoSage: AI-Powered Repository Intelligence")

# Sidebar for Ingestion
with st.sidebar:
    st.header("Repositories")
    repo_url = st.text_input("GitHub Repo URL", placeholder="https://github.com/user/repo")
    
    if st.button("Ingest Repo"):
        if repo_url:
            with st.spinner("Ingesting repository... This may take a few minutes."):
                try:
                    response = requests.post(f"{settings.API_URL}/ingest", json={"repo_url": repo_url})
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"Indexed successfully! Repo ID: {data['repo_id']}")
                        st.session_state['repo_id'] = data['repo_id']
                        # Reset chat messages so AI context doesn't contaminate across repos
                        st.session_state['messages'] = []
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection error: {e}")
        else:
            st.warning("Please enter a valid GitHub repository URL.")
            
    if 'repo_id' in st.session_state:
        st.info(f"Active Repo ID:\n{st.session_state['repo_id']}")

# Main Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("references"):
            with st.expander("View Reference Files"):
                for ref in message["references"]:
                    st.markdown(f"**{ref['file']}** (`{ref['function']}`, Lines {ref['lines']})")

if prompt := st.chat_input("Ask a question about the codebase (e.g. 'Where is auth handled?')"):
    if 'repo_id' not in st.session_state:
        st.error("Please ingest a repository first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing codebase..."):
                try:
                    chat_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1][-5:]]
                    payload = {"repo_id": st.session_state['repo_id'], "question": prompt, "chat_history": chat_history}
                    response = requests.post(f"{settings.API_URL}/query", json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        answer = data.get("answer", "No answer found.")
                        references = data.get("references", [])
                        
                        st.markdown(answer)
                        if references:
                            with st.expander("View Reference Files"):
                                for ref in references:
                                    st.markdown(f"**{ref['file']}** (`{ref['function']}`, Lines {ref['lines']})")
                                    
                        st.session_state.messages.append({"role": "assistant", "content": answer, "references": references})
                    else:
                        st.error(f"Error querying: {response.text}")
                        st.session_state.messages.pop()
                except Exception as e:
                    st.error(f"Connection error: {e}")
                    st.session_state.messages.pop()
