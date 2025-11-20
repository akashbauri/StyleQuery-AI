import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from config import config
from few_shot_prompts import few_shot_prompts
import streamlit as st

class LLMHandler:
    def __init__(self):
        # Configure Gemini API
        genai.configure(api_key=config.GEMINI_API_KEY)
        
        # Initialize Gemini via LangChain
        self.llm = ChatGoogleGenerativeAI(
            model=config.MODEL_NAME,
            google_api_key=config.GEMINI_API_KEY,
            temperature=config.TEMPERATURE,
            convert_system_message_to_human=True
        )
        
        # Initialize embeddings for ChromaDB
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=config.GEMINI_API_KEY
        )
        
        # Initialize ChromaDB vector store
        self.vectorstore = None
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Create ChromaDB vector store from few-shot examples"""
        try:
            # Convert few-shot prompts to documents
            documents = []
            for i, example in enumerate(few_shot_prompts):
                doc = Document(
                    page_content=example['Question'],
                    metadata={
                        'sql_query': example['SQLQuery'],
                        'visualization': example['Visualization'],
                        'index': i
                    }
                )
                documents.append(doc)
            
            # Create ChromaDB vector store
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                collection_name="few_shot_examples"
            )
            
        except Exception as e:
            st.error(f"ChromaDB initialization failed: {e}")
    
    def get_similar_examples(self, question: str, k: int = 3):
        """Retrieve k most similar few-shot examples using ChromaDB"""
        try:
            similar_docs = self.vectorstore.similarity_search(question, k=k)
            examples = []
            
            for doc in similar_docs:
                examples.append({
                    'Question': doc.page_content,
                    'SQLQuery': doc.metadata['sql_query'],
                    'Visualization': doc.metadata['visualization']
                })
            
            return examples
        except Exception as e:
            st.error(f"Error retrieving examples: {e}")
            return []
    
    def generate_sql(self, user_question: str):
        """Generate SQL query from natural language using few-shot learning"""
        
        # Get similar examples from ChromaDB
        similar_examples = self.get_similar_examples(user_question, k=config.TOP_K)
        
        # Build few-shot examples text
        examples_text = "\n\n".join([
            f"Question: {ex['Question']}\nSQL: {ex['SQLQuery']}\nVisualization: {ex['Visualization']}"
            for ex in similar_examples
        ])
        
        # Create prompt template
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
        
        # Create LLM chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            # Generate response
            response = chain.run(examples=examples_text, question=user_question)
            
            # Parse response
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

# Create singleton instance
llm_handler = LLMHandler()
