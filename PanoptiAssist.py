import openai
import streamlit as st
import time

assistant_id = st.secrets["ASSISTANT_KEY_PANOPTICASSIST"]

client = openai

if "start_chat" not in st.session_state:
    st.session_state.start_chat = False
if "thread_id" not in st.session_state:
    st.session_state.thread_id = None
if "buttons_shown" not in st.session_state:
    st.session_state.buttons_shown = False
if "prompt" not in st.session_state:
    st.session_state.prompt = ""
if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

st.set_page_config(page_title="PanoptiAssist", page_icon=":shield:")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# Sidebar logo removed
# st.sidebar.image("/Users/khandelwal/Desktop/ProductUnfiltered_LOGO copy.png", use_column_width=True)  # Ensure the path is correct

st.sidebar.title("Tell us about your interests")

# New user inputs
topic = st.sidebar.selectbox("What do you want to learn today?", 
                             ["Cloud Native Application Security Solution", "Attack Path Analysis", "Code & CI/CD Security", 
                              "Kubernetes Security", "Cloud Security Posture Management (CSPM)", "Cloud Workload Protection (CWP)", 
                              "API Security", "CIEM Solutions"], index=0)
expertise = st.sidebar.selectbox("What is your level of expertise?", 
                                 ["Associate", "Foundational", "Professional", "Specialist"])
role = st.sidebar.selectbox("What is your role?", 
                            ["Application Developer", "Cloud Architect", "Chief Information Security Officer (CISO)", 
                             "Compliance Officer", "DevOps", "DevSecOps", "IT Operations", "SecOps"])

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown(
    "<div style='text-align: center; color: grey; font-size: small;'>"
    "MVP built with ❤️ by <a href='https://drive.google.com/file/d/1CJFOagkuCkYqZnDTC1w32f6-KSnhKwxx/view?usp=sharing' target='_blank'><b>Utkarsh Khandelwal</b></a>,<br>Former intern at Cisco Outshift"
    "</div>", 
    unsafe_allow_html=True
)

if st.sidebar.button("Start Chat"):
    st.session_state.start_chat = True
    st.session_state.topic = topic
    st.session_state.expertise = expertise
    st.session_state.role = role
    st.session_state.buttons_shown = False  # Reset buttons_shown when starting a new chat
    
    # Create a thread for the chat
    thread = client.beta.threads.create()
    st.session_state.thread_id = thread.id
    
    # Get enthusiastic message
    introduction_prompt = (
        f"The user is interested in learning about {topic}, has an expertise level of {expertise}, "
        f"and their role is {role}. Please greet the user, introduce yourself, and then explain the available features and assistance. "
        "Keep it short and enthusiastic."
    )
    
    client.beta.threads.messages.create(
        thread_id=st.session_state.thread_id,
        role="user",
        content=introduction_prompt
    )
    
    run = client.beta.threads.runs.create(
        thread_id=st.session_state.thread_id,
        assistant_id=assistant_id,
    )

    while run.status != 'completed':
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run.id
        )
    messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    # Process and display introduction message
    assistant_messages_for_run = [
        message for message in messages
        if message.run_id == run.id and message.role == "assistant"
    ]
    if assistant_messages_for_run:
        st.session_state.recommendation = assistant_messages_for_run[0].content[0].text.value

st.title("PanoptiAssist - Your AI Cloud Security Assistant")
st.write("Hello! I'm here to help you simplify complex cloud security concepts and provide detailed insights into Panoptica's features.")

if st.button("Exit Chat"):
    st.session_state.messages = []  # Clear the chat history
    st.session_state.start_chat = False  # Reset the chat state
    st.session_state.thread_id = None
    st.session_state.buttons_shown = False  # Reset buttons_shown on exiting chat

def typing_effect(text):
    for char in text:
        yield char
        time.sleep(0.004)

if st.session_state.start_chat:
    if "openai_model" not in st.session_state:
        st.session_state.openai_model = "gpt-3.5-turbo"
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Initial assistant message
    if not st.session_state.messages:
        # Display the enthusiastic message if available
        if st.session_state.recommendation:
            enthusiastic_message = st.session_state.recommendation
            st.session_state.messages.append({"role": "assistant", "content": enthusiastic_message})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(enthusiastic_message))

        # Message-2: Inquiry message
        inquiry_message = (
            "You can also inquire about specific topics or details you're interested in learning more about."
        )
        st.session_state.messages.append({"role": "assistant", "content": inquiry_message})
        with st.chat_message("assistant"):
            st.write_stream(typing_effect(inquiry_message))

    # Add predefined buttons only at the start
    if not st.session_state.buttons_shown:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("What types of cloud environments does Panoptica support?"):
                st.session_state.prompt = "What types of cloud environments does Panoptica support?"
                st.session_state.buttons_shown = True
            if st.button("What educational resources does Cisco Panoptica offer for users?"):
                st.session_state.prompt = "What educational resources does Panoptica offer for users?"
                st.session_state.buttons_shown = True
            if st.button("What is Panoptica's Cloud Security Posture Management (CSPM)?"):
                st.session_state.prompt = "What is Cloud Security Posture Management (CSPM)?"
                st.session_state.buttons_shown = True
        with col2:
            if st.button("What API security features does Cisco Panoptica offer?"):
                st.session_state.prompt = "What API security features does Panoptica offer?"
                st.session_state.buttons_shown = True
            if st.button("How does Panoptica's attack path analysis work?"):
                st.session_state.prompt = "How does Panoptica's attack path analysis work?"
                st.session_state.buttons_shown = True
            if st.button("What kind of AI-powered insights does Panoptica provide?"):
                st.session_state.prompt = "What kind of AI-powered insights does Panoptica provide?"
                st.session_state.buttons_shown = True

    if st.session_state.prompt:
        st.session_state.messages.append({"role": "user", "content": st.session_state.prompt})
        with st.chat_message("user"):
            st.markdown(st.session_state.prompt)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=st.session_state.prompt
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))

        st.session_state.prompt = ""

    # User input
    if user_input := st.chat_input("How can I assist you with cloud security or Panoptica features?"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=user_input
        )

        run = client.beta.threads.runs.create(
            thread_id=st.session_state.thread_id,
            assistant_id=assistant_id,
        )

        while run.status != 'completed':
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=st.session_state.thread_id,
                run_id=run.id
            )
        messages = client.beta.threads.messages.list(
            thread_id=st.session_state.thread_id
        )

        # Process and display assistant messages
        assistant_messages_for_run = [
            message for message in messages
            if message.run_id == run.id and message.role == "assistant"
        ]
        for message in assistant_messages_for_run:
            st.session_state.messages.append({"role": "assistant", "content": message.content[0].text.value})
            with st.chat_message("assistant"):
                st.write_stream(typing_effect(message.content[0].text.value))

else:
    st.write("Please provide your interests in the sidebar and click 'Start Chat' to begin.")
