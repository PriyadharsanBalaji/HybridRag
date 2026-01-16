"""
Main Streamlit Application
Hybrid RAG System with Beautiful UI
"""

import streamlit as st
from pathlib import Path
import time
from typing import List
from loguru import logger

# Import all components
from config import settings
from src.document_processor import document_processor
from src.vector_store import vector_store
from src.knowledge_graph import knowledge_graph
from src.rag_chain import rag_chain
from src.llm_manager import llm_manager
from utils.validators import FileValidator, QueryValidator
from utils.helpers import format_file_size, sanitize_filename
from utils.metrics import metrics_tracker
from ui.styles import get_custom_css
from ui.components import (
    render_header, render_stat_card, render_source_card,
    render_metrics_dashboard, render_info_box
)
from ui.visualizations import render_knowledge_graph


# Page configuration
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'uploaded_files' not in st.session_state:
        st.session_state.uploaded_files = []
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False


def process_uploaded_files(files: List) -> bool:
    """Process uploaded files"""
    try:
        total_chunks = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, uploaded_file in enumerate(files):
            # Update progress
            progress = (idx + 1) / len(files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save file
            file_path = settings.UPLOADS_DIR / sanitize_filename(uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process document
            chunks = document_processor.process_document(file_path)
            
            # Add to vector store
            vector_store.add_chunks(chunks)
            
            # Add to knowledge graph
            if settings.ENABLE_KNOWLEDGE_GRAPH:
                knowledge_graph.add_chunks(chunks)
            
            total_chunks += len(chunks)
            
            # Track
            st.session_state.uploaded_files.append({
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'chunks': len(chunks)
            })
        
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        
        # Update metrics
        metrics_tracker.total_documents_processed += len(files)
        
        logger.info(f"Processed {len(files)} files, created {total_chunks} chunks")
        return True
        
    except Exception as e:
        logger.error(f"Error processing files: {e}")
        st.error(f"Error processing files: {str(e)}")
        return False


def render_sidebar():
    """Render sidebar with controls"""
    with st.sidebar:
        st.title("⚙️ Control Panel")
        
        # File upload
        st.header("📤 Upload Documents")
        uploaded_files = st.file_uploader(
            "Choose files",
            type=["pdf", "docx", "txt", "md", "csv", "xlsx", "pptx", "html"],
            accept_multiple_files=True,
            help="Upload documents to build your knowledge base"
        )
        
        if uploaded_files:
            # Validate files
            valid_files = []
            for file in uploaded_files:
                is_valid, error = FileValidator.validate_file(file.name, file.size)
                if is_valid:
                    valid_files.append(file)
                else:
                    st.error(f"❌ {file.name}: {error}")
            
            if valid_files and st.button("🚀 Process Files", key="process"):
                with st.spinner("Processing documents..."):
                    if process_uploaded_files(valid_files):
                        st.success(f"✅ Successfully processed {len(valid_files)} files!")
                        st.session_state.processing_complete = True
                        st.rerun()
        
        st.divider()
        
        # System stats
        st.header("📊 System Stats")
        
        # Vector store stats
        vector_stats = vector_store.get_stats()
        st.metric("📄 Documents in Vector DB", vector_stats.get('total_documents', 0))
        
        # Graph stats
        if settings.ENABLE_KNOWLEDGE_GRAPH:
            graph_stats = knowledge_graph.get_stats()
            st.metric("🔗 Graph Nodes", graph_stats.get('total_nodes', 0))
            st.metric("↔️ Graph Edges", graph_stats.get('total_edges', 0))
        
        # Rate limit stats
        rate_stats = llm_manager.get_rate_limit_stats()
        st.metric(
            "🔥 API Calls (Today)",
            f"{rate_stats.get('day_used', 0)}/{rate_stats.get('day_limit', 0)}"
        )
        st.metric(
            "⚡ API Calls (Minute)",
            f"{rate_stats.get('minute_used', 0)}/{rate_stats.get('minute_limit', 0)}"
        )
        
        st.divider()
        
        # Settings
        st.header("⚙️ Settings")
        
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=settings.TEMPERATURE,
            step=0.1,
            help="Higher = more creative, Lower = more focused"
        )
        settings.TEMPERATURE = temperature
        
        top_k = st.slider(
            "Top K Results",
            min_value=1,
            max_value=10,
            value=settings.TOP_K_VECTOR_RESULTS,
            help="Number of results to retrieve"
        )
        settings.TOP_K_VECTOR_RESULTS = top_k
        
        st.divider()
        
        # Reset button
        if st.button("🗑️ Reset System", type="secondary"):
            if st.checkbox("Are you sure?"):
                vector_store.reset()
                knowledge_graph.reset()
                st.session_state.chat_history = []
                st.session_state.uploaded_files = []
                st.success("System reset successfully!")
                st.rerun()


def render_main_content():
    """Render main content area"""
    
    # Header
    render_header()
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Chat",
        "📚 Documents",
        "🕸️ Knowledge Graph",
        "📈 Analytics"
    ])
    
    # TAB 1: Chat Interface
    with tab1:
        st.subheader("Ask Questions About Your Documents")
        
        # Chat history display
        chat_container = st.container()
        with chat_container:
            for chat in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(chat['query'])
                with st.chat_message("assistant"):
                    st.write(chat['answer'])
                    
                    # Show sources in expander
                    if chat.get('sources'):
                        with st.expander("📎 View Sources"):
                            for idx, source in enumerate(chat['sources'], 1):
                                render_source_card(source, idx)
        
        # Query input
        user_query = st.chat_input("Ask a question about your documents...")
        
        if user_query:
            # Validate query
            is_valid, error = QueryValidator.validate_query(user_query)
            
            if not is_valid:
                st.error(error)
            else:
                # Check if documents are loaded
                vector_stats = vector_store.get_stats()
                if vector_stats.get('total_documents', 0) == 0:
                    st.warning("⚠️ Please upload documents first!")
                else:
                    # Display user message
                    with st.chat_message("user"):
                        st.write(user_query)
                    
                    # Generate response
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            result = rag_chain.query(user_query)
                            
                            # Display answer
                            st.write(result['answer'])
                            
                            # Display metrics
                            if result.get('metrics'):
                                with st.expander("📊 Query Metrics"):
                                    render_metrics_dashboard(result['metrics'])
                            
                            # Display sources
                            if result.get('sources'):
                                with st.expander(f"📎 Sources ({len(result['sources'])})"):
                                    for idx, source in enumerate(result['sources'], 1):
                                        render_source_card(source, idx)
                    
                    # Save to history
                    st.session_state.chat_history.append({
                        'query': user_query,
                        'answer': result['answer'],
                        'sources': result.get('sources', [])
                    })
    
    # TAB 2: Documents
    with tab2:
        st.subheader("📚 Uploaded Documents")
        
        if st.session_state.uploaded_files:
            for file_info in st.session_state.uploaded_files:
                with st.expander(f"📄 {file_info['name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Size:** {format_file_size(file_info['size'])}")
                    with col2:
                        st.write(f"**Chunks:** {file_info['chunks']}")
        else:
            render_info_box(
                "No documents uploaded yet. Use the sidebar to upload files.",
                "info"
            )
    
    # TAB 3: Knowledge Graph
    with tab3:
        st.subheader("🕸️ Knowledge Graph Visualization")
        
        if settings.ENABLE_KNOWLEDGE_GRAPH:
            graph_data = knowledge_graph.get_visualization_data()
            
            if graph_data['nodes']:
                st.info(f"📊 Showing {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
                render_knowledge_graph(graph_data)
            else:
                render_info_box(
                    "Knowledge graph is empty. Upload documents to build the graph.",
                    "info"
                )
        else:
            st.warning("Knowledge graph is disabled in settings.")
    
    # TAB 4: Analytics
    with tab4:
        st.subheader("📈 System Analytics")
        
        # Overall metrics
        avg_metrics = metrics_tracker.get_average_metrics()
        
        if avg_metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_stat_card(
                    "Total Queries",
                    metrics_tracker.total_queries,
                    "💬"
                )
            
            with col2:
                render_stat_card(
                    "Documents Processed",
                    metrics_tracker.total_documents_processed,
                    "📄"
                )
            
            with col3:
                render_stat_card(
                    "Avg Response Time",
                    f"{avg_metrics.get('avg_total_time', 0):.2f}s",
                    "⚡"
                )
            
            with col4:
                render_stat_card(
                    "Avg Retrieval Time",
                    f"{avg_metrics.get('avg_retrieval_time', 0):.2f}s",
                    "🔍"
                )
            
            # Display summary
            st.markdown("### 📊 Performance Summary")
            st.code(metrics_tracker.get_summary())
        else:
            render_info_box(
                "No analytics available yet. Start asking questions!",
                "info"
            )


def main():
    """Main application entry point"""
    try:
        # Initialize
        initialize_session_state()
        
        # Render UI
        render_sidebar()
        render_main_content()
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: #888;'>
                🤖 Hybrid RAG System v1.0 | Powered by Gemini AI, ChromaDB & NetworkX
            </div>
            """,
            unsafe_allow_html=True
        )
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
