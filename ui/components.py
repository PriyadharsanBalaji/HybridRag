"""
Reusable UI Components
"""

import streamlit as st
from typing import List, Dict, Any


def render_header():
    """Render application header"""
    st.markdown(
        """
        <div class="main-header">
            🤖 Hybrid RAG System
        </div>
        <div class="sub-header">
            Powered by Vector Search + Knowledge Graph + Gemini AI
        </div>
        """,
        unsafe_allow_html=True
    )


def render_stat_card(label: str, value: Any, icon: str = "📊"):
    """Render a statistics card"""
    st.markdown(
        f"""
        <div class="stats-card">
            <div class="stat-number">{icon} {value}</div>
            <div class="stat-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_source_card(source: Dict[str, Any], index: int):
    """Render a source citation card"""
    source_type = source.get('type', 'Unknown')
    
    if source_type == 'Vector Search':
        content = f"""
        <div class="source-card">
            <h4>📄 Source {index}: {source.get('file', 'Unknown')}</h4>
            <p><strong>Type:</strong> Vector Search</p>
            <p><strong>Page:</strong> {source.get('page', 'N/A')}</p>
            <p><strong>Similarity:</strong> {source.get('similarity', 'N/A')}</p>
            <p><strong>Preview:</strong> {source.get('content', '')[:150]}...</p>
        </div>
        """
    else:  # Knowledge Graph
        content = f"""
        <div class="source-card">
            <h4>🔗 Source {index}: Knowledge Graph</h4>
            <p><strong>Entity:</strong> {source.get('entity', 'Unknown')}</p>
            <p><strong>Type:</strong> {source.get('label', 'Unknown')}</p>
            <p><strong>Related:</strong> {source.get('neighbors', 'None')}</p>
        </div>
        """
    
    st.markdown(content, unsafe_allow_html=True)


def render_metrics_dashboard(metrics: Dict[str, Any]):
    """Render metrics dashboard"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_stat_card(
            "Retrieval Time",
            f"{metrics.get('retrieval_time', 0):.2f}s",
            "⚡"
        )
    
    with col2:
        render_stat_card(
            "Generation Time",
            f"{metrics.get('generation_time', 0):.2f}s",
            "🤖"
        )
    
    with col3:
        render_stat_card(
            "Vector Results",
            metrics.get('vector_results', 0),
            "📊"
        )
    
    with col4:
        render_stat_card(
            "Graph Results",
            metrics.get('graph_results', 0),
            "🔗"
        )


def render_info_box(message: str, box_type: str = "info"):
    """Render colored info box"""
    st.markdown(
        f'<div class="{box_type}-box">{message}</div>',
        unsafe_allow_html=True
    )


def render_chat_message(message: str, is_user: bool = False):
    """Render chat message bubble"""
    message_class = "user-message" if is_user else "assistant-message"
    st.markdown(
        f'<div class="{message_class}">{message}</div>',
        unsafe_allow_html=True
    )
