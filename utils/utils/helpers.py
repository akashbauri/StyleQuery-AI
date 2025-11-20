import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_visualization(df, viz_type, query):
    """Create appropriate visualization based on type and data"""
    
    if df is None or df.empty:
        st.warning("No data to visualize")
        return
    
    try:
        if viz_type == 'number':
            # Single metric display
            value = df.iloc[0, 0]
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.metric(label="Result", value=f"{value:,.0f}" if isinstance(value, (int, float)) else value)
        
        elif viz_type == 'bar_chart':
            # Bar chart
            if len(df.columns) >= 2:
                fig = px.bar(
                    df, 
                    x=df.columns[0], 
                    y=df.columns[1],
                    title="Distribution",
                    color=df.columns[1],
                    color_continuous_scale='Blues'
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == 'pie_chart':
            # Pie chart
            if len(df.columns) >= 2:
                fig = px.pie(
                    df,
                    names=df.columns[0],
                    values=df.columns[1],
                    title="Distribution"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == 'table':
            # Table display
            st.dataframe(df, use_container_width=True)
        
        else:
            # Default: show table
            st.dataframe(df, use_container_width=True)
    
    except Exception as e:
        st.error(f"Visualization error: {e}")
        st.dataframe(df, use_container_width=True)

def format_sql_query(query):
    """Format SQL query for better readability"""
    keywords = ['SELECT', 'FROM', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT', 'AND', 'OR']
    formatted = query
    for keyword in keywords:
        formatted = formatted.replace(keyword, f'\n{keyword}')
    return formatted.strip()
