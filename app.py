import streamlit as st
import pandas as pd
from database import db_manager
from llm_handler import llm_handler
from utils.helpers import create_visualization, format_sql_query
from web_search import web_search_fallback

# Page configuration
st.set_page_config(
    page_title="StyleQuery AI",
    page_icon="👔",
    layout="wide"
)

# Title and description
st.title("👔 Clothing Brand Analysis - AI Assistant")
st.markdown("Ask questions about your clothing inventory in natural language!")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    This AI-powered tool allows you to query your clothing inventory database using natural language.
    
    **Technologies:**
    - Gemini 2.0 Flash
    - LangChain
    - ChromaDB
    - MySQL
    - Plotly
    
    **Examples:**
    - "How many Nike shirts do we have?"
    - "Show me top brands by stock"
    - "What's the total value of Adidas products?"
    """)
    
    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"], use_container_width=True)
        if "visualization" in message:
            create_visualization(
                message["dataframe"],
                message["viz_type"],
                message.get("sql_query", "")
            )

# Chat input
if prompt := st.chat_input("Ask about your inventory..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Generate SQL query
            sql_query, viz_type = llm_handler.generate_sql(prompt)
            
            if sql_query:
                # Show generated SQL
                with st.expander("🔍 Generated SQL Query"):
                    st.code(format_sql_query(sql_query), language="sql")
                
                # Execute query
                result_df = db_manager.execute_query(sql_query)
                
                if result_df is not None and not result_df.empty:
                    # Display results
                    st.success("✅ Query executed successfully!")
                    
                    # Show data table
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Create visualization
                    create_visualization(result_df, viz_type, sql_query)
                    
                    # Save to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "✅ Query executed successfully!",
                        "dataframe": result_df,
                        "viz_type": viz_type,
                        "sql_query": sql_query,
                        "visualization": True
                    })
                else:
                    st.warning("No results found for your query.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No results found."
                    })
            else:
                # Fallback to web search
                st.info("🌐 This question seems outside the database scope. Searching the web...")
                web_result = web_search_fallback(prompt)
                st.markdown(web_result)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": web_result
                })
