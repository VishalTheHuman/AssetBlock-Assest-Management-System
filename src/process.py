"""

Assuming the database = "AssetBlock" is already created using pgAdmin4


'''

SCHEMA

'''

Table 1: ASSET_DATA

Columns:
- uid: string 
    Unique identifier for each record.
    
- email: string (Foreign Key)
    Foreign key referencing the email of the user who uploaded the file.
    
- hashvalue: string (Primary Key)
    Hash value of the file data.
    
- filename : string
    Stores the name of the file.
    
- file: bytea
    Binary data of the file.
    
- status: enum ["Accepted", "Under Review", "Rejected"]
    Status of the file (accepted, under review, or rejected).
    
- date: date
    Date when the file was uploaded.
    
- time: time [without time zone]
    Time when the file was uploaded (without time zone).
    
- file_type: enum ["Document", "Certificate", "License"]
    Type of the file (document, certificate, or license).
    

"""

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from constants import ASSET_DATA_SCHEMA, STATUS_ENUM, FILE_TYPE_ENUM

load_dotenv()

def getConnection(database_name="AssetBlock"):
    try:
        conn = psycopg2.connect(
            database=database_name,
            user=os.getenv("POSTGRE_USER"),
            host="localhost",
            password=os.getenv("POSTGRE_PASSWORD"),
            port=5432
        )
        return conn
    except psycopg2.DatabaseError as e:
        print(f"Database connection error: {e}")
        return None


def tableExists(table_name="ASSET_DATA", schema="public"):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute(
                sql.SQL("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s)"),
                (schema, table_name)
            )
            exists = cur.fetchone()[0]
            print(f"Table {table_name} exists: {exists}")
            return exists
    except psycopg2.Error as e:
        print(f"Error checking table existence: {e}")
        return False
    finally:
        if conn:
            conn.close()

def getAllAdmin():
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            command = f"SELECT uid, email, hashvalue, filename, status, date, time, file_type FROM ASSET_DATA WHERE status = 'Under Review'"
            cur.execute(command)
            rows = cur.fetchall()
            return rows
    except psycopg2.DatabaseError as e:
        print(f"Error querying data: {e}")
        return []
    finally:
        if conn:
            conn.close()

def doesHashExist(hash_value):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT 1 FROM ASSET_DATA WHERE hashvalue = %s)", (hash_value,))
            exists = cur.fetchone()[0]
            print(f"Hash {hash_value} exists: {exists}")
            return True
    except psycopg2.Error as e:
        print(f"Error checking hash existence: {e}")
        return False
    finally:
        if conn:
            conn.close()
            

def transferOwnership(hashvalue, user_uid, recipient_uid):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE ASSET_DATA SET uid = %s WHERE hashvalue = %s AND uid = %s",
                (recipient_uid, hashvalue, user_uid)
            )
            if cur.rowcount == 0:
                print(f"No record found with hashvalue: {hashvalue} and uid: {user_uid}")
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error transferring ownership: {e}")
        return False
    finally:
        if conn:
            conn.close()


def createTable():
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute(STATUS_ENUM)
            print("Status enum created or already exists.")
            cur.execute(FILE_TYPE_ENUM)
            print("File type enum created or already exists.")
            cur.execute(ASSET_DATA_SCHEMA)
            print("Table creation command executed.")
            conn.commit()
            print("Table and ENUM types created successfully.")
    except psycopg2.DatabaseError as e:
        print(f"Error creating table: {e}")
        
        
def insertToAssetData(uid, email, hashvalue, filename, file, status, date, time, file_type):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            insert_query = """
            INSERT INTO ASSET_DATA (uid, email, hashvalue, filename, file, status, date, time, file_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
            """
            cur.execute(insert_query, (uid, email, hashvalue, filename, psycopg2.Binary(file), status, date, time, file_type))
            conn.commit()
            print("Data inserted successfully.")
        return True
    except psycopg2.DatabaseError as e:
        print(f"Error inserting data: {e}")
        return False

def getByParam(param="uid", value="", file_type="", status=""):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            command = f"SELECT uid, email, hashvalue, filename, status, date, time, file_type FROM ASSET_DATA WHERE {param} = %s"
            params = [value]
            
            if file_type:
                command += " AND file_type = %s"
                params.append(file_type)
            
            if status:
                command += " AND status = %s"
                params.append(status)
            
            cur.execute(command, params)
            rows = cur.fetchall()
            return rows
    except psycopg2.DatabaseError as e:
        print(f"Error querying data: {e}")
        return []
    finally:
        if conn:
            conn.close()
            
def deleteFileByHash(hash_value):
    try: 
        conn = getConnection()
        with conn.cursor() as cur:
            sql = "DELETE FROM ASSET_DATA WHERE hashvalue = %s"
            cur.execute(sql, (hash_value,))
            conn.commit()
            print(f"File with hash {hash_value} deleted successfully.")
        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False
    finally:
        if conn:
            conn.close()
        
def getFile(hash_value):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute(f"SELECT filename, file FROM ASSET_DATA WHERE hashvalue = '{hash_value}';")
            row = cur.fetchone()
            return row
    except psycopg2.DatabaseError as e:
        print(f"Error querying data: {e}")
        return []
    finally:
        if conn:
            conn.close()

def changeStatus(hashvalue, status):
    try:
        conn = getConnection()
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE ASSET_DATA SET status = %s WHERE hashvalue = %s",
                (status, hashvalue)
            )
            if cur.rowcount == 0:
                print(f"No record found with hashvalue: {hashvalue} and status: {status}")
                return False
            conn.commit()
            return True
    except psycopg2.Error as e:
        print(f"Error transferring ownership: {e}")
        return False
    finally:
        if conn:
            conn.close()

def initialize():
    conn = getConnection()
    if conn is None:
        print("Connection could not be established")
        return

    try:
        tableExists_before = tableExists(conn)
        print(f"Table exists before creation attempt: {tableExists_before}")
        if not tableExists_before:
            print("Table does not exist, creating table...")
            createTable()
            tableExists_after = tableExists(conn)
            print(f"Table exists after creation attempt: {tableExists_after}")
        else:
            print("Table already exists")
    finally:
        pass

if __name__ == "__main__":
    initialize()
