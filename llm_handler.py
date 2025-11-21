import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import config
from few_shot_prompts import few_shot_prompts
import streamlit as st

class LLMHandler:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        self.llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            google_api_key=config.GEMINI_API_KEY,
            temperature=config.TEMPERATURE,
            convert_system_message_to_human=True
        )
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=config.GEMINI_API_KEY
        )
        
        # Store examples in memory instead of ChromaDB for now
        self.examples = few_shot_prompts
    
    def get_similar_examples(self, question: str, k: int = 3):
        """Return first k examples (simplified for deployment)"""
        return self.examples[:k]
    
    def generate_sql(self, user_question: str):
        """Generate SQL query from natural language"""
        
        similar_examples = self.get_similar_examples(user_question, k=config.TOP_K)
        
        examples_text = "\n\n".join([
            f"Question: {ex['Question']}\nSQL: {ex['SQLQuery']}\nVisualization: {ex['Visualization']}"
            for ex in similar_examples
        ])
        
        prompt_template = """You are an expert SQL query generator for a clothing inventory database.

Database Schema:
Table: clothing_data
Columns: SKU, Brand, Category, Color, Size, Price_INR, Stock, Material, Gender

Here are some example questions and their SQL queries:

{examples}

Now generate a SQL query for this question:
Question: {question}

Return ONLY the SQL query and visualization type in this exact format:
SQL: <your sql query>
VISUALIZATION: <number|bar_chart|pie_chart|table>

SQL:"""

        prompt = PromptTemplate(
            input_variables=["examples", "question"],
            template=prompt_template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            response = chain.run(examples=examples_text, question=user_question)
            
            sql_query = ""
            viz_type = "table"
            
            lines = response.strip().split('\n')
            for line in lines:
                if line.strip().startswith('SELECT') or line.strip().startswith('select'):
                    sql_query = line.strip()
                elif 'VISUALIZATION:' in line.upper():
                    viz_type = line.split(':')[-1].strip().lower()
            
            return sql_query, viz_type
            
        except Exception as e:
            st.error(f"SQL generation failed: {e}")
            return None, None

llm_handler = LLMHandler()
