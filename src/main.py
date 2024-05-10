from markdowns import DESCRIPTION
import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
from dotenv import load_dotenv
import json
import requests
import os

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
        
        return auth.get_user_by_email(email=email).uid
    except:
        return None

def auth_page():  
    st.set_page_config(page_title="AssetBlock", page_icon="📄")
    show_pages(
        [
            Page("src/main.py", "Authentication", icon="🔒"),
            Page("src/pages/dashboard.py", "Dashboard", icon="🏠"),
        ]
    )
    hide_pages(["Dashboard"])
    initialize()
    st.title(":red[Asset]:orange[Block] 📄", anchor = False)
    st.markdown("### **```Description```**")
    st.markdown(DESCRIPTION)
    
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
        if submit_login:
            if email and password:
                uid = login(email, password)
                if uid is not None:
                    st.session_state["uid"] = uid
                    st.switch_page("pages/dashboard.py")
                    hide_pages(["Authentication"])
                    show_pages(["Dashboard"])
                else:
                    st.error("Enter a vaild E-mail and Password", icon= "🚨")

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
                uid  = signup(email,password,username)
                if uid is not None:
                    st.session_state["uid"] = uid
                    st.switch_page("pages/dashboard.py")
                    hide_pages(["Authentication"])
                    show_pages(["Dashboard"])
                else:
                    st.error("Username Already exists (or) Email already used by another user", icon= "🚨")    
    
def main(): 
    auth_page()
    initialize()
    

if __name__ == "__main__":
    main()