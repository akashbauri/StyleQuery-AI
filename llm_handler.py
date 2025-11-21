from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config import config
from few_shot_prompts import few_shot_prompts
import streamlit as st

class LLMHandler:
    def __init__(self):
        # Initialize Groq Chat Model
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            groq_api_key=config.GROQ_API_KEY,
            temperature=config.TEMPERATURE
        )
        
        # Store few-shot examples in session
        self.few_shot_examples = few_shot_prompts
    
    def get_similar_examples(self, question: str, top_k: int = 3):
        """Simple keyword-based matching for few-shot examples"""
        question_lower = question.lower()
        scored_examples = []
        
        for example in self.few_shot_examples:
            score = 0
            example_lower = example['question'].lower()
            
            # Count matching words
            question_words = set(question_lower.split())
            example_words = set(example_lower.split())
            common_words = question_words.intersection(example_words)
            score = len(common_words)
            
            if score > 0:
                scored_examples.append((score, example))
        
        # Sort by score and return top_k
        scored_examples.sort(reverse=True, key=lambda x: x[0])
        return [ex[1] for ex in scored_examples[:top_k]]
    
    def generate_sql(self, question: str):
        """Generate SQL query from natural language question"""
        try:
            # Get similar examples
            similar_examples = self.get_similar_examples(question, config.TOP_K)
            
            # Build few-shot examples string
            examples_text = "\n\n".join([
                f"Question: {ex['question']}\nSQL: {ex['sql']}"
                for ex in similar_examples
            ])
            
            # Create prompt
            prompt_template = f"""You are an expert SQL query generator for a clothing inventory database.

Database Schema:
Table: clothing_data
Columns:
- SKU (TEXT): Unique product identifier
- Brand (TEXT): Brand name (Nike, Adidas, Puma, etc.)
- Category (TEXT): Product type (Shirt, Jeans, Shoes, etc.)
- Color (TEXT): Product color
- Size (TEXT): Size (XS, S, M, L, XL, XXL)
- Price_INR (INTEGER): Price in Indian Rupees
- Stock (INTEGER): Available quantity
- Material (TEXT): Fabric/material type
- Gender (TEXT): Target gender (Men, Women, Unisex)

Few-shot Examples:
{examples_text}

Now generate a SQL query for this question:
Question: {{question}}

IMPORTANT RULES:
1. Return ONLY the SQL query, no explanations
2. Use proper SQL syntax for MySQL
3. Always use SELECT statements
4. For counting, use COUNT(*)
5. For aggregations, use appropriate GROUP BY
6. Column names are case-sensitive
7. Use LIMIT when showing top results

SQL:"""
            
            prompt = PromptTemplate(
                input_variables=["question"],
                template=prompt_template
            )
            
            # Create chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate SQL
            response = chain.run(question=question)
            sql_query = response.strip()
            
            # Clean up the SQL query
            if sql_query.startswith('```sql'):
                sql_query = sql_query[6:]
            if sql_query.startswith('```'):
                sql_query = sql_query[3:]
            if sql_query.endswith('```'):
                sql_query = sql_query[:-3]
            
            sql_query = sql_query.strip()
            
            return sql_query
            
        except Exception as e:
            st.error(f"Error generating SQL: {str(e)}")
            return None

llm_handler = LLMHandler()
