import requests
from config import config
import streamlit as st

def web_search_fallback(query):
    """Fallback to web search if query is not database-related"""
    
    if not config.get('SERPER_API_KEY'):
        return "Web search is not configured. Please set SERPER_API_KEY."
    
    try:
        url = "https://google.serper.dev/search"
        payload = {"q": query}
        headers = {
            'X-API-KEY': config.get('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers)
        results = response.json()
        
        if 'organic' in results and len(results['organic']) > 0:
            top_result = results['organic'][0]
            return f"**{top_result['title']}**\n\n{top_result['snippet']}\n\nSource: {top_result['link']}"
        
        return "No relevant results found."
        
    except Exception as e:
        return f"Web search failed: {e}"
