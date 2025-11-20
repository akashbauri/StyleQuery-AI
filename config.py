import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

class Config:
    @staticmethod
    def get(key: str, default=None):
        try:
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
        except:
            pass
        return os.getenv(key, default)
    
    @property
    def GEMINI_API_KEY(self):
        return self.get('GEMINI_API_KEY')
    
    @property
    def DB_HOST(self):
        return self.get('DB_HOST', 'localhost')
    
    @property
    def DB_PORT(self):
        return int(self.get('DB_PORT', 3306))
    
    @property
    def DB_USER(self):
        return self.get('DB_USER', 'root')
    
    @property
    def DB_PASSWORD(self):
        return self.get('DB_PASSWORD')
    
    @property
    def DB_NAME(self):
        return self.get('DB_NAME', 'cloth_brand_analysis')
    
    @property
    def TEMPERATURE(self):
        return float(self.get('TEMPERATURE', 0.1))
    
    @property
    def TOP_K(self):
        return int(self.get('TOP_K', 3))
    
    @property
    def MODEL_NAME(self):
        return "gemini-2.0-flash-exp"

config = Config()
