import streamlit as st
from openai import OpenAI
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.title("ChatGPT-3.5 with Vision")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you today?"}]

supported_file_types = ['txt', 'py', 'js', 'java', 'c', 'cpp', 'cs', 'html', 'htm', 'css']

file = st.file_uploader("Attach files", type=supported_file_types)
st.write("Currently only one file is accepted")

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if file is None:
    prompt = st.chat_input("Message ChatGPT-3.5")
    if prompt:
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model='gpt-3.5-turbo-0125',
                messages=[{"role": "system", "content": "You are ChatGPT-3.5, now with the capability to read {supported_file_types} files. Remember, you cannot read any other file types."}] +
                            [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]],
                stream=True,
            ):
                incremental_content = response.choices[0].delta.content or ""
                full_response += incremental_content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        st.session_state["messages"].append({"role": "assistant", "content": full_response})
elif file is not None:
    prompt = st.chat_input("Message ChatGPT-3.5")
    if prompt:
        file_name = file.name
        file_content = ""
        extension = os.path.splitext(file_name)[1].strip('.')
        if extension in ['txt', 'py', 'js', 'java', 'c', 'cpp', 'cs', 'html', 'htm', 'css']:
            file_content = file.getvalue().decode("utf-8")

        st.session_state["messages"].append({"role": "user", "content": f"""{file.name} was attached to this message...\n{prompt}"""})
        with st.chat_message("user"):
            st.markdown(f"""{file.name} was attached to this message...\n\n{prompt}""")

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model='gpt-3.5-turbo-0125',
                messages=[{"role": "system", "content": f"You are ChatGPT-3.5, now with the capability to read {supported_file_types} files. Remember, you cannot read any other file types. The user has currently attached a file called '{file_name}'. Use its contents as context and answer any questions they may have. Here they are: {file_content}"}] +
                            [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]],
                stream=True,
            ):
                incremental_content = response.choices[0].delta.content or ""
                full_response += incremental_content
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

        st.session_state["messages"].append({"role": "assistant", "content": full_response})
