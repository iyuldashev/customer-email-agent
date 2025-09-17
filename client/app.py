import streamlit as st
import pickle
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

st.title("Customer Support Email Agent - Gmail Manager")

# Initialize session state
if 'connected_accounts' not in st.session_state:
    st.session_state.connected_accounts = []

def connect_gmail(account_name):
    """Connect a Gmail account"""
    token_file = f'token_{account_name}.pickle'
    
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    
    with open(token_file, 'wb') as token:
        pickle.dump(creds, token)
    
    st.session_state.connected_accounts.append(account_name)
    st.success(f"Connected {account_name} successfully!")

def disconnect_gmail(account_name):
    """Disconnect a Gmail account"""
    token_file = f'token_{account_name}.pickle'
    if os.path.exists(token_file):
        os.remove(token_file)
    
    st.session_state.connected_accounts.remove(account_name)
    st.success(f"Disconnected {account_name}")

# UI Components
st.header("Connect Gmail Account")
account_name = st.text_input("Account Name/Identifier")

if st.button("Connect Account"):
    if account_name:
        connect_gmail(account_name)
    else:
        st.error("Please enter an account name")

st.header("Connected Accounts")
if st.session_state.connected_accounts:
    for account in st.session_state.connected_accounts:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text(account)
        with col2:
            if st.button(f"Disconnect", key=f"disc_{account}"):
                disconnect_gmail(account)
else:
    st.info("No accounts connected yet")