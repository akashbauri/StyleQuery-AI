import mysql.connector
from mysql.connector import Error
import pandas as pd
from config import config
import streamlit as st

class DatabaseManager:
    def __init__(self):
        self.config = {
            'host': config.DB_HOST,
            'port': config.DB_PORT,
            'user': config.DB_USER,
            'password': config.DB_PASSWORD,
            'database': config.DB_NAME,
            'autocommit': True
        }
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                return True
        except Error as e:
            st.error(f"Database connection failed: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query: str):
        try:
            if not self.connection or not self.connection.is_connected():
                if not self.connect():
                    return None
            
            df = pd.read_sql(query, self.connection)
            return df
            
        except Error as e:
            st.error(f"Query execution failed: {e}")
            return None

db_manager = DatabaseManager()
