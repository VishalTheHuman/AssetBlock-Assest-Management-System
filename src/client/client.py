import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from constants import DESCRIPTION_MARKDOWN
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import json
import requests
from st_pages import show_pages, Page, hide_pages

load_dotenv()

REST_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"

@st.cache_data
def initialize():
    firebase_admin.initialize_app(credentials.Certificate("src/firebase.json"))


def signup(email, password, username):
    try:
        user = auth.create_user(email = email, password = password, uid = username)
        return user.uid
    except (firebase_admin._auth_utils.UidAlreadyExistsError, firebase_admin.auth.EmailAlreadyExistsError):
        return None

def doesUserExist(uid):
    try:
        auth.get_user(uid)
        return True
    except:
        return False

def login(email, password, return_secure_token = True):
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
        user = auth.get_user_by_email(email=email)
        return user.uid, user.email 
    except:
        return None

def auth_page():  
    st.set_page_config(page_title="AssetBlock", page_icon="📄")
    show_pages(
        [
            Page("src/client/client.py", "Authentication", icon="🔒"),
            Page("src/client/pages/dashboard.py", "Dashboard", icon="🏠"),
            Page("src/client/pages/search.py", "Search", icon="🔍"), 
            Page("src/client/pages/request.py", "Request", icon="📬")
        ]
    )
    hide_pages(["Dashboard", "Search", "Request", "Blockchain"])
    initialize()
    st.title(":red[Asset]:orange[Block] 📄", anchor = False)
    st.markdown("### **```Description```**")
    st.markdown(DESCRIPTION_MARKDOWN)
    
    font_css = """
            <style>
            button[data-baseweb="tab"] {
            margin: 0;
            width: 100%;

            }
            </style>
            """

    st.write(font_css, unsafe_allow_html=True)

    
    LOGIN, SIGNUP = st.tabs(["**Login 🔐**", "**Sign Up ✍**"])
    
    with LOGIN:
               
        c_login = st.container(border=True)
        text = st.empty()
        email = c_login.text_input(
            label = "Email", 
            placeholder = "Enter your E-mail ", 
            key="email_login", 
        )
        password = c_login.text_input(
            label = "Enter a password", 
            placeholder = "Enter your Password ",
            type="password",
            key = "password_login", 
        )
        submit_login = c_login.button(
            "Login",
            use_container_width = True, 
            type="primary"
        )
        uid = None
        if submit_login:
            if email and password:
                try:
                    uid, email = login(email, password)
                except:
                    st.error("Enter a vaild E-mail and Password.", icon= "🚨")
                
                if uid is not None:
                    st.session_state["uid"] = uid
                    st.session_state["email"] = email
                    st.switch_page("pages/dashboard.py")
                    show_pages(["Dashboard", "Search", "Request"])
                
                    
    with SIGNUP:
        c_signup = st.container(border = True)
        username = c_signup.text_input(
            label = "Username", 
            placeholder="Enter your Username",
            key="username",
        )
        email = c_signup.text_input(
            label = "Email", 
            placeholder = "Enter your E-mail ", 
            key = "email_signup",
        )
        password = c_signup.text_input(
            label = "Password", 
            placeholder = "Enter your Password (Min : 6 Characters)",
            type="password",
            key = "password_signup" ,
        )
        submit_signup = c_signup.button(
            "Sign Up",
            use_container_width = True, 
            type="primary"
        )
        if submit_signup:
            if username and password and email:
                try:
                    uid, email  = signup(email,password,username)
                    if uid is not None:
                        st.session_state["uid"] = uid
                        st.session_state["email"] = email
                        st.switch_page("pages/dashboard.py")
                    else:
                        st.error("Username Already exists (or) Email already used by another user", icon= "🚨")
                except:
                    st.error("Username Already exists (or) Email already used by another user", icon= "🚨")
   

def main(): 
    auth_page()
    initialize()
    

if __name__ == "__main__":
    main()