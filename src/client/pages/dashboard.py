import streamlit as st
import base64
import requests 

API_URL = "http://127.0.0.1:8000/"

def dashboard():
    st.set_page_config(page_title="Dashboard - AssetBlock", page_icon="🏡")
    st.title(":orange[Dashboard] 🏡", anchor = False)
    st.markdown(f"##### **Hello :orange[@{st.session_state.uid}] !**")
    file_type = st.selectbox("Select File Configuration", [
        "All", 
        "Document", 
        "Certificate", 
        "License"
    ])
    container = st.container(border=True)
    param = {}
    if file_type != "All":
        param["file_type"] = file_type
    data = requests.get(API_URL + f"allfiles/{st.session_state.uid}").json()
    if data["status_code"] == 200:
        for i in range(data["count"]):
            if file_type == "All" or data["file_type"][i] == file_type:
                result_object = container.container(border=True)      
                result_object.markdown(f"""
                **📂:orange[File Name :]** {data["filename"][i]}  
                **🪪:orange[UID :]** {data["uid"][i]}  
                **📧:orange[Email :]** {data["email"][i]}  
                **#️⃣:orange[Hash Value :]** {data["hashvalue"][i]}  
                **🧧:orange[File Type :]** {data["file_type"][i]}  
                **📆:orange[Upload Time :]** {data["date"][i]}  {data["time"][i]}  
                **🗽:orange[Status :]** {data["status"][i]} 
                """)   
                file_data = base64.b64decode(requests.get(API_URL+f"getfile/{data["hashvalue"][i]}", params = param).json()["file"])
                result_object.download_button(
                    "Download", 
                    type="primary", 
                    file_name=data["filename"][i],
                    data = file_data,
                    use_container_width = True,
                    key=f"button_{i}")
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
        container.error("No files found",icon="🚨")

    
if __name__ == "__main__":
    if "uid" in st.session_state:
        dashboard()