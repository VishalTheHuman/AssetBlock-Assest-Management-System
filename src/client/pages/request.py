import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import base64

API_URL = "http://127.0.0.1:8000/"

from client import doesUserExist

def request():
    st.set_page_config(page_title="Request - AssetBlock", page_icon="📬")


    st.title(":orange[Request] 📬", anchor = False)
    addasset = st.container(border=True)
    addasset.markdown("### :red[Add an Asset] 📄")
    FILE = addasset.file_uploader("Choose a file", type=["pdf", "docx", "txt", "png", "jpg", "jpeg"], accept_multiple_files=False)
    if FILE:
        file_type = addasset.selectbox("File Type", [
            "Document", 
            "Certificate", 
            "License"
        ])
    
    if FILE:
        file_name = addasset.text_input("File Name",value=FILE.name)
    submit = addasset.button(
        "**Submit Request 📬**",
        use_container_width = True, 
        type="primary"
    )
    
    if submit:
        if FILE:
            ret = requests.post(API_URL+f"insert/data", json={
                "email" : st.session_state.email, 
                "uid" : st.session_state.uid, 
                "filename" : file_name, 
                "file" : base64.b64encode(FILE.read()).decode('utf-8'), 
                "file_type" : file_type
                }).json()
            if ret["status_code"]==200:
                st.success("File Uploded Successfully")
            else:
                st.error("Failed to upload as the file has already been issued.", icon="🚨")
                
        else:
            st.error("Upload a File to create an Add Request", icon="🚨")
            
    transferasset = st.container(border=True)
    transferasset.markdown("### :blue[Transfer an Asset] 🔁")
    transferasset.markdown("**```Note :```**  Find the hash of the file to tranfer either from the dashboard or through search page 🔎")
    transfer_hash = transferasset.text_input(
        label = "File's Hash",
        placeholder="Enter File's Hash")
    transfer_uid = transferasset.text_input(
        "Recipient's UID", 
        placeholder="Enter Recipient UID"
    )
    transfer = transferasset.button(
        "**Transfer Request 🔁**",
        use_container_width = True, 
        type="primary"
    )
    if transfer:
        if transfer_hash and transfer_uid: 
            file_status = requests.get(API_URL + f"fileexists/{transfer_hash}").json()
            if doesUserExist(transfer_uid) and  file_status["status"]=="Exists":
                ret = requests.put(API_URL + f"tranferownership/{transfer_hash}/{transfer_uid}/{st.session_state.uid}").json()
                if ret["status"] == "done":
                    st.success(f"Successfully Transferred to {transfer_uid}", icon="✅")
                else:
                    st.error("Transfer Failed !", icon = "🚨")
            else:
                st.error("Enter a Valid Hash and Recipient UID", icon="🚨")
        else:
            st.error("Enter both Hash Value and Recipient UID", icon="🚨")
    
if __name__ == "__main__":
    if "uid" in st.session_state:
        request()