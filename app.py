"""Module for handling auto-response features using Streamlit and the Gmail API."""

import os
import shelve
import time
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from gmail_manager import GmailManager  # Assuming this is your custom module for email management

# Load environment variables
load_dotenv()

client = OpenAI(api_key=st.secrets["OPEN_AI_KEY"])


def send_email(to, mail_subject, mail_body):
    """Send email to the specified recipient with a subject and body.

    Args:
        to (str): Recipient's email address.
        mail_subject (str): Subject of the email.
        mail_body (str): Body of the email.
    """
    gmail_client = GmailManager()
    gmail_client.send_email("blake@blakeamtech.com", to, mail_subject, mail_body)


def load_chat_history():
    """Load and return the chat history from a shelve file.

    Returns:
        list: List of stored chat messages.
    """
    with shelve.open("chat_history") as chat_db:
        return chat_db.get("messages", [])


def save_chat_history(messages):
    """Save the chat history to a shelve file.

    Args:
        messages (list): List of chat messages to save.
    """
    with shelve.open("chat_history") as chat_db:
        chat_db["messages"] = messages


# Streamlit title and setup
st.title("Email With Ease")

# Sidebar for Email Sending
with st.sidebar:
    st.title("Send Email")
    password = st.text_input("Invite Code")
    recipient_email = st.text_input("Recipient Email")
    email_subject = st.text_input("Subject")
    email_body = st.text_area("Message")
    if st.button("Send Email"):
        if password == st.secrets["EMAIL_PASSWORD"]:
            send_email(recipient_email, email_subject, email_body)
            st.success("Email sent successfully!")
        else:
            st.success("Did you enter the invite code?")
    if st.button("Clear Messages"):
        st.session_state.messages = []

# Main chat interface setup
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Chat input
user_input = st.text_input("Enter an email you need to respond to or a prompt for an email:", "")
st.write('''
    **Ever needed to send an email from your company's customer service address but couldn't get access?**
    
    **Struggling to write emails that sound like your CEO?**
    
    Our tool has you covered. 
         
    Send emails from any preregistered email with ease, using a model fine-tuned to mimic your CEO's writing style. Perfect for crafting flawless emails, even when you're locked out of your company's email system.
    ''')
if st.button("Submit"):
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call to OpenAI API
    COMPLETION = client.chat.completions.create(
        model="ft:gpt-3.5-turbo-0125:techograms::9jWj2X7v",
        messages=[
            {
                "role": "system",
                "content": "Blake is a friendly machine learning engineer.",
            },
            {"role": "user", "content": user_input},
        ],
    )
    response = COMPLETION.choices[0].message.content

    # Simulate typing animation
    message_container = st.empty()
    for i in range(1, len(response) + 1):
        message_container.write(f"You: {response[:i]}")
        time.sleep(0.01)  # Adjust timing to suit the desired typing speed

    st.session_state.messages.append({"role": "bot", "content": response})
    save_chat_history(st.session_state.messages)
    message_container.write(f"You: {response}")  # Finally display the full response
    
