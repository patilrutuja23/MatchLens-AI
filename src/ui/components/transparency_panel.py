"""
Transparency Panel Component
Shows AI reasoning, sources, and confidence for explainability
"""

import streamlit as st
from typing import Dict, List, Optional


def render_transparency_panel(
    ai_response: str,
    retrieved_docs: Optional[List[Dict]] = None,
    confidence: Optional[float] = None,
    reasoning_steps: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    metadata: Optional[Dict] = None
):
    """
    Render transparency panel showing AI reasoning and sources
    
    Args:
        ai_response: The AI-generated response
        retrieved_docs: List of retrieved documents with relevance scores
        confidence: Confidence score (0-1)
        reasoning_steps: List of reasoning steps taken
        sources: List of source documents used
        metadata: Additional metadata
    """
    
    st.markdown("---")
    st.subheader("🔍 Transparency & Explainability")
    st.caption("See exactly how this answer was generated")
    
    # Create tabs for different transparency aspects
    tabs = st.tabs(["📊 Overview", "📚 Retrieved Documents", "🧠 Reasoning", "📖 Sources"])
    
    # Tab 1: Overview
    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if confidence is not None:
                confidence_pct = confidence * 100
                color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🟠"
                st.metric(
                    "Confidence Score",
                    f"{confidence_pct:.0f}%",
                    delta=f"{color} {'High' if confidence > 0.8 else 'Medium' if confidence > 0.6 else 'Low'}"
                )
            else:
                st.metric("Confidence Score", "N/A")
        
        with col2:
            doc_count = len(retrieved_docs) if retrieved_docs else 0
            st.metric("Documents Retrieved", doc_count)
        
        with col3:
            source_count = len(sources) if sources else 0
            st.metric("Sources Used", source_count)
        
        # Show method used
        if metadata:
            st.info(f"**Method:** {metadata.get('method', 'AI Generation')}")
            if metadata.get('rag_enabled'):
                st.success("✅ RAG-Enhanced Response (Real document retrieval)")
            else:
                st.warning("⚠️ Basic Mode (No document retrieval)")
    
    # Tab 2: Retrieved Documents
    with tabs[1]:
        if retrieved_docs and len(retrieved_docs) > 0:
            st.markdown("### Retrieved Evidence")
            st.caption("Documents retrieved from knowledge base to answer your question")
            
            for i, doc in enumerate(retrieved_docs, 1):
                relevance = doc.get('relevance', doc.get('score', 0))
                # Convert distance to relevance if needed
                if relevance > 1:
                    relevance = 1 / (1 + relevance)
                
                relevance_pct = relevance * 100
                
                # Color code by relevance
                if relevance_pct >= 80:
                    color = "🟢"
                    badge = "Highly Relevant"
                elif relevance_pct >= 60:
                    color = "🟡"
                    badge = "Relevant"
                else:
                    color = "🟠"
                    badge = "Somewhat Relevant"
                
                with st.expander(f"{color} **Document {i}** - {doc.get('source', 'Unknown Source')} ({relevance_pct:.0f}% {badge})"):
                    # Show source
                    st.markdown(f"**Source:** {doc.get('source', 'Unknown')}")
                    st.markdown(f"**Relevance:** {relevance_pct:.1f}%")
                    
                    # Show rank if available
                    if 'rank' in doc:
                        st.markdown(f"**Rank:** #{doc['rank']}")
                    
                    # Show text
                    st.markdown("**Content:**")
                    text = doc.get('text', doc.get('content', 'No content available'))
                    st.markdown(f"> {text}")
                    
                    # Show metadata if available
                    if 'metadata' in doc:
                        with st.expander("📋 Document Metadata"):
                            st.json(doc['metadata'])
        else:
            st.info("ℹ️ No documents were retrieved for this response.")
            st.caption("This response was generated without document retrieval. Consider enabling RAG for more accurate, source-backed answers.")
    
    # Tab 3: Reasoning Steps
    with tabs[2]:
        st.markdown("### AI Reasoning Process")
        st.caption("Step-by-step breakdown of how the answer was generated")
        
        if reasoning_steps and len(reasoning_steps) > 0:
            for i, step in enumerate(reasoning_steps, 1):
                st.markdown(f"**Step {i}:**")
                st.write(step)
                if i < len(reasoning_steps):
                    st.markdown("↓")
        else:
            # Generate default reasoning steps
            st.markdown("**Step 1:** Query Analysis")
            st.write("Analyzed the user's question to understand intent and required information.")
            
            st.markdown("↓")
            
            st.markdown("**Step 2:** Information Retrieval")
            if retrieved_docs:
                st.write(f"Retrieved {len(retrieved_docs)} relevant documents from knowledge base.")
            else:
                st.write("Generated response using language model knowledge.")
            
            st.markdown("↓")
            
            st.markdown("**Step 3:** Response Generation")
            st.write("Synthesized information into a coherent, educational explanation.")
            
            st.markdown("↓")
            
            st.markdown("**Step 4:** Quality Check")
            if confidence:
                st.write(f"Validated response quality (Confidence: {confidence*100:.0f}%)")
            else:
                st.write("Validated response for accuracy and clarity.")
    
    # Tab 4: Sources
    with tabs[3]:
        st.markdown("### Source Documents")
        st.caption("Official documents used to generate this response")
        
        if sources and len(sources) > 0:
            st.markdown("**Documents Referenced:**")
            for source in sources:
                st.markdown(f"- 📄 {source}")
            
            st.info("💡 All sources are official FIFA, IFAB, or VAR protocol documents.")
        else:
            st.warning("⚠️ No specific source documents were used.")
            st.caption("This response was generated from the AI model's training data. For source-backed answers, ensure RAG is enabled and documents are ingested.")
        
        # Add download option for sources
        if sources:
            st.markdown("---")
            st.markdown("**Want to verify?**")
            st.caption("You can download and review the original source documents.")


def render_mini_transparency(
    confidence: Optional[float] = None,
    doc_count: int = 0,
    rag_enabled: bool = False
):
    """
    Render a compact transparency indicator
    
    Args:
        confidence: Confidence score
        doc_count: Number of documents retrieved
        rag_enabled: Whether RAG was used
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if confidence:
            color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🟠"
            st.caption(f"{color} Confidence: {confidence*100:.0f}%")
        else:
            st.caption("⚪ Confidence: N/A")
    
    with col2:
        st.caption(f"📚 Documents: {doc_count}")
    
    with col3:
        if rag_enabled:
            st.caption("✅ RAG-Enhanced")
        else:
            st.caption("⚠️ Basic Mode")


def render_confidence_badge(confidence: float):
    """
    Render a confidence badge
    
    Args:
        confidence: Confidence score (0-1)
    """
    confidence_pct = confidence * 100
    
    if confidence >= 0.9:
        st.success(f"✅ Very High Confidence ({confidence_pct:.0f}%)")
    elif confidence >= 0.8:
        st.success(f"✅ High Confidence ({confidence_pct:.0f}%)")
    elif confidence >= 0.7:
        st.info(f"ℹ️ Good Confidence ({confidence_pct:.0f}%)")
    elif confidence >= 0.6:
        st.warning(f"⚠️ Moderate Confidence ({confidence_pct:.0f}%)")
    else:
        st.error(f"❌ Low Confidence ({confidence_pct:.0f}%)")


# Made with Bob