import streamlit as st
import requests
import base64
 

API_URL = "http://127.0.0.1:8000/"


def search():
    st.set_page_config(page_title="Search - AssetBlock", page_icon="🔍")
    st.title(":orange[Search] 🔍", anchor = False)
    
    container = st.container(border=True)
    mode = container.selectbox("Select Search Configuration", [
        "Hash Value", 
        "User Identifier (UID)", 
        "File Name", 
        "Email"
    ])
    
    data = None
    match mode:
        case "Hash Value":
            info = container.text_input("Enter the Hash Value : ", placeholder="Hash Value")
        case "User Identifier (UID)":
            info = container.text_input("Enter User Identifier (UID) : ",placeholder="User Identification (UID)")
        case "File Name":
            info = container.text_input("Enter File Name : ", placeholder="File Name")
        case "Email":
            info = container.text_input("Enter Email : ", placeholder="Email")
    
    if mode != "Hash Value":  
        file_type = container.selectbox("Select Search Configuration", [
            "All", 
            "Document", 
            "Certificate", 
            "License"
        ])
    else:
        file_type = ""
    
    
    submit = container.button(
        "**Search 🔎**",
        use_container_width = True, 
        type="primary"
    )
    
    if submit:
        if info:
            info = info.strip()
            to_add = {"status" : ""}
            if file_type !="All":
                to_add["file_type"] =  file_type
            match mode:
                case "Hash Value":
                    data = requests.get(API_URL+f"getfilebyhash/{info}", params = to_add).json()
                case "User Identifier (UID)":
                    data = requests.get(API_URL+f"getfilesbyuid/{info}", params = to_add).json()
                case "File Name":
                    data = requests.get(API_URL+f"getfilesbyname/{info}", params = to_add).json()
                case "Email":
                    data = requests.get(API_URL+f"getfilesbyemail/{info}", params = to_add).json()
        
    if data:
        if data["status_code"] == 200:
            content = []
            results = st.container(border=True)
            if data["count"] == 1:
                results.markdown(f"### Found {data["count"]} File")
            else:
                results.markdown(f"### Found {data["count"]} Files")
            for i in range(data["count"]):
                result_object = results.container(border=True)      
                result_object.markdown(f"""
                **📂:orange[File Name :]** {data["filename"][i]}  
                **🪪:orange[UID :]** {data["uid"][i]}  
                **📧:orange[Email :]** {data["email"][i]}  
                **#️⃣:orange[Hash Value :]** {data["hashvalue"][i]}  
                **🧧:orange[File Type :]** {data["file_type"][i]}  
                **📆:orange[Upload Time :]** {data["date"][i]}  {data["time"][i]}  
                **🗽:orange[Status :]** {data["status"][i]} 
                """)   
                file_data = base64.b64decode(requests.get(API_URL+f"getfile/{data["hashvalue"][i]}").json()["file"])
                result_object.download_button(
                    "Download", 
                    type="primary", 
                    file_name=data["filename"][i],
                    data = file_data,
                    use_container_width = True,
                    key=f"button_{i}")
                if data["uid"][i] == st.session_state.uid:
                    delete_button = result_object.button(
                        "Delete File ❌", 
                        use_container_width=True,
                        key=f"delete_{i}"

                    )
                    if delete_button:
                        ret = requests.post(API_URL + f"deletefile/{data["hashvalue"][i]}").json()
                        if ret["status"] == 200:
                            result_object.success("File deleted Successfully", icon="✅")
                        else:
                            result_object.error("File can't be deleted", icon="🚨")
        else:
            st.error("No file has been found", icon="🚨")
        
if __name__ == "__main__":
    if "uid" in st.session_state:
        search()
        