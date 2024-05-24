import streamlit as st
import requests
import base64

API_URL = "http://127.0.0.1:8000/"

STATUS_MAP = {
    "Accepted": 0,
    "Under Review": 1,
    "Rejected": 2
}

def dashboard():
    st.set_page_config(page_title="Admin Dashboard - AssetBlock", page_icon="🏡")
    st.title(":orange[Dashboard] 🏡", anchor = False)
    st.markdown(f"##### **Hello :orange[Admin] !**")
    
    data = requests.get(API_URL + "getall").json()
    if data:
        if data["status_code"] == 200:
            content = []
            results = st.container()
            results.markdown(f"###  {data['count']} File{'s' if data['count'] > 1 else ''} Pending Review....")
            for i in range(data["count"]):
                result_object = results.container(border=True)
                result_object.markdown(f"""
                **📂:orange[File Name :]** {data["filename"][i]}  
                **🪪:orange[UID :]** {data["uid"][i]}  
                **📧:orange[Email :]** {data["email"][i]}  
                **#️⃣:orange[Hash Value :]** {data["hashvalue"][i]}  
                **🧧:orange[File Type :]** {data["file_type"][i]}  
                **📆:orange[Upload Time :]** {data["date"][i]} {data["time"][i]}  
                **🗽:orange[Status :]** {data["status"][i]} 
                """)
                
                file_data = base64.b64decode(requests.get(API_URL + f"getfile/{data['hashvalue'][i]}").json()["file"])
                result_object.download_button(
                    "Download",
                    file_name=data["filename"][i],
                    data=file_data,
                    use_container_width=True,
                    key=f"button_{i}"
                )
                
                def changeStatus(hashvalue=data["hashvalue"][i], index=i):
                    new_status = st.session_state[f"status_{index}"]
                    ret = requests.put(API_URL + f"changestatus/{hashvalue}/{new_status}").json()
                    if ret["status"] == 200:
                        st.success("File Access Modified Successfully", icon="✅")
                    else:
                        st.error("File Status can't be Modified", icon="🚨")
                
                status = result_object.selectbox(
                    "Modify the status:",
                    ["Accepted", "Under Review", "Rejected"],
                    index=STATUS_MAP[data["status"][i]],
                    key=f"status_{i}",
                    on_change=changeStatus
                )
                
                def deleteFile(hashvalue=data["hashvalue"][i], index=i):
                    ret = requests.post(API_URL + f"deletefile/{hashvalue}").json()
                    if ret["status"] == 200:
                        st.success("File deleted Successfully", icon="✅")
                        st.experimental_rerun()
                    else:
                        st.error("File can't be deleted", icon="🚨")
                
                result_object.button(
                    "Delete File 🚫",
                    use_container_width=True,
                    key=f"delete_{i}",
                    on_click=deleteFile, 
                    type="primary"
                )
        else:
            st.success("No file has been found", icon="🚨")
        
if __name__ == "__main__":
    if "uid" in st.session_state:
        dashboard()