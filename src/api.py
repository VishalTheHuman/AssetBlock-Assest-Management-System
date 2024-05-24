from fastapi import FastAPI, HTTPException, Query
from process import *
from pydantic import BaseModel
from datetime import datetime
from collections import defaultdict
import base64
import os
import sys
from typing import Optional


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sha256 import sha256
from firebase_admin import credentials, auth


app = FastAPI()

class DataModel(BaseModel):
    email: str
    uid: str
    filename: str
    file: str
    file_type: str
    

REST_API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"


def initialize():
    firebase_admin.initialize_app(credentials.Certificate("src/firebase.json"))


def doesUserExist(uid):
    try:
        initialize()
        auth.get_user(uid)
        return True
    except :
        return False


@app.post("/deletefile/{hashvalue}")
async def deletefile(hashvalue):
    if deleteFileByHash(hashvalue):
        return {
            "status" : 200
        }
    return {
        "status" : 424
    }
    

@app.get("/getall")
async def getAll():
    data = getAllAdmin()
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/allfiles/{uid}")
async def allFiles(uid):
    data = getByParam("uid", uid)
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/fileexists/{hash_value}")
async def fileexists(hash_value : str):
    return {
        "status" : "Exists" if doesHashExist(hash_value) else "Doesn't Exists"
    }


@app.get("/getfilesbyuid/{uid}")
async def getfilesbyuid(uid:str, file_type:Optional[str] = Query(None), status : Optional[str] = Query(None)):
    data = getByParam("uid", uid, file_type if file_type else "", status if status else "" )
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/getfilebyhash/{hash_value}")
async def getfilebyhash(hash_value : str):
    data = getByParam("hashvalue", hash_value)
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/getfilesbyname/{name}")
async def getfilesbyname(name:str, file_type:Optional[str] = Query(None), status : Optional[str] = Query(None)):
    data = getByParam("filename", name, file_type if file_type else "", status if status else "")
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/getfilesbyemail/{email}")
async def getfilesbyemail(email : str, file_type:Optional[str] = Query(None), status : Optional[str] = Query(None)):
    data = getByParam("email", email, file_type if file_type and file_type!="All" else "", status if status else "")
    if not data:
        return HTTPException(status_code=404, detail="Email not found")
    return processData(data)


@app.get("/getfile/{hash_value}")
async def getfile(hash_value : str):
    data = getFile(hash_value)
    if not data:
        return HTTPException(status_code=404, detail="Not found")
    return {
        "filename" : data[0],
        "file" : base64.b64encode(data[1]).decode('utf-8'), 
        "status_code" : 200
    }


@app.post("/insert/data")
async def insertData(data: DataModel):
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M:%S")
    if insertToAssetData(data.uid, data.email, sha256(data.file), data.filename, base64.b64decode(data.file), "Under Review", current_date, current_time, data.file_type):

        return {"message": "Data inserted successfully", "status_code":200}
    else:
        return {"message": "Data inserted successfully", "status_code":424}


@app.put("/tranferownership/{hash_value}/{tranfer_uid}/{user_uid}")
async def tranferownership(hash_value : str, tranfer_uid, user_uid):
    if transferOwnership(hash_value, user_uid, tranfer_uid):
        return {
            "status" : "done"
        }
    else:
        return {
            "status" : "failed"
        }


@app.put("/changestatus/{hashvalue}/{status}")
async def changestatus(hashvalue, status):
    if changeStatus(hashvalue, status):
        return {
            "status" : 200
        }
    else:
        return {
            "status" : 424
        }
    
        
def processData(data):
    out = defaultdict(list)
    for uid, email, hashvalue, filename, status, date, time, file_type in data:
        out["uid"].append(uid)
        out["email"].append(email)
        out["hashvalue"].append(hashvalue)
        out["filename"].append(filename)
        out["status"].append(status)
        out["date"].append(date)
        out["time"].append(time)
        out["file_type"].append(file_type)
    out["count"] = len(data)
    out["status_code"] = 200
    return out