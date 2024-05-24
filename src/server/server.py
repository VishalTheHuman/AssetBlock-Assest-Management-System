import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import DESCRIPTION_MARKDOWN
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from st_pages import show_pages, Page, hide_pages
from dotenv import load_dotenv
import json
import requests

load_dotenv()

REST_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

@st.cache_data
def initialize():
    firebase_admin.initialize_app(credentials.Certificate("src/firebase.json"))


def login(email, password, return_secure_token = True):
    load_dotenv()
    try:
        r = requests.post(
            REST_API_URL,
            params={
                "key": os.getenv("FIREBASE_WEB_API_KEY")
            },
            data=json.dumps({
                "email": email,
                "password": password,
                "returnSecureToken": return_secure_token
            })
        ).json()
        if "error" in r:
            return None
        
        return auth.get_user_by_email(email=email).uid
    except:
        return None


def main():
    st.set_page_config(page_title="Admin - AssetBlock", page_icon="📄")
    initialize()
    show_pages(
        [
            Page("src/server/server.py", "Authentication", icon="🔒"),
            Page("src/server/pages/dashboard.py", "Dashboard", icon="🏠"),
            Page("src/server/pages/search.py", "Search", icon="🔍")
        ]
    )
    hide_pages(["Dashboard", "Search", "Blockchain"])
    
    st.title(":red[Asset]:orange[Block] 📄", anchor = False)
    st.markdown("### **```Description```**")
    st.markdown(DESCRIPTION_MARKDOWN)
    LOGIN = st.tabs(["**Login 🔐**"])[0]
    font_css = """
            <style>
            button[data-baseweb="tab"] {
            margin: 0;
            width: 100%;

            }
            </style>
            """

    st.write(font_css, unsafe_allow_html=True)
    with LOGIN:
        c_login = st.container(border=True)
        text = st.empty()
        email = c_login.text_input(
            label = "Email", 
            placeholder = "Enter your E-mail ", 
        )
        password = c_login.text_input(
            label = "Enter a password", 
            placeholder = "Enter your Password ",
            type="password",
        )
        submit_login = c_login.button(
            "Login",
            use_container_width = True, 
            type="primary"
        )
        if submit_login:
            if email and password:
                uid = login(email, password)
                if uid is not None and uid=="admin":
                    st.session_state["uid"] = uid
                    st.switch_page("pages/dashboard.py")
                    show_pages(["Dashboard", "Blockchain", "Search"])
                else:
                    st.error("Enter a vaild E-mail and Password", icon= "🚨")
                    
if __name__ == "__main__":
    main()
    initialize()