import streamlit as st
import pandas as pd
from database import db_manager
from llm_handler import llm_handler
from web_search import web_search_fallback
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="StyleQuery AI",
    page_icon="👔",
    layout="wide"
)

# Helper function for visualization (moved inline)
def create_visualization(df, viz_type):
    """Create visualization based on type"""
    if df is None or df.empty:
        st.warning("No data to visualize")
        return
    
    try:
        if viz_type == 'number':
            value = df.iloc[0, 0]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.metric(label="Result", value=f"{value:,.0f}" if isinstance(value, (int, float)) else value)
        
        elif viz_type == 'bar_chart':
            if len(df.columns) >= 2:
                fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == 'pie_chart':
            if len(df.columns) >= 2:
                fig = px.pie(df, names=df.columns[0], values=df.columns[1], title="Distribution")
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.dataframe(df, use_container_width=True)
    
    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.dataframe(df, use_container_width=True)

# Title
st.title("👔 StyleQuery AI")
st.markdown("### Ask Your Fashion Inventory Anything")
st.caption("Powered by Gemini 2.0 • LangChain • MySQL")

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.write("""
    Query your clothing inventory using natural language.
    
    **Examples:**
    - "How many Nike shirts?"
    - "Show top brands by stock"
    - "What's the total value of Adidas?"
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Initialize chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"], use_container_width=True)
        if "visualization" in message:
            create_visualization(message["dataframe"], message["viz_type"])

# Chat input
if prompt := st.chat_input("Ask about your inventory..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            sql_query, viz_type = llm_handler.generate_sql(prompt)
            
            if sql_query:
                with st.expander("🔍 Generated SQL"):
                    st.code(sql_query, language="sql")
                
                result_df = db_manager.execute_query(sql_query)
                
                if result_df is not None and not result_df.empty:
                    st.success("✅ Query executed!")
                    st.dataframe(result_df, use_container_width=True)
                    create_visualization(result_df, viz_type)
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "✅ Query executed!",
                        "dataframe": result_df,
                        "viz_type": viz_type,
                        "visualization": True
                    })
                else:
                    st.warning("No results found.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "No results found."
                    })
            else:
                st.info("🌐 Searching the web...")
                web_result = web_search_fallback(prompt)
                st.markdown(web_result)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": web_result
                })
