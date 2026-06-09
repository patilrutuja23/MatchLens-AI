"""
RAG Chain for MatchLens AI
Orchestrates retrieval and generation for enhanced explanations
"""

from typing import Dict, List, Optional, Tuple
from src.utils.retriever import DocumentRetriever
from src.utils.granite_client import GraniteClient


class RAGChain:
    """Retrieval-Augmented Generation chain for football analysis"""
    
    def __init__(
        self,
        retriever: Optional[DocumentRetriever] = None,
        llm_client: Optional[GraniteClient] = None
    ):
        """
        Initialize RAG chain
        
        Args:
            retriever: Document retriever instance
            llm_client: LLM client instance
        """
        self.retriever = retriever or DocumentRetriever()
        self.llm_client = llm_client or GraniteClient()
        
        # Load all available indices
        self.retriever.load_all_indices()
        
        print(f"✅ RAG Chain initialized")
    
    def retrieve_context(
        self,
        query: str,
        doc_types: List[str] = None,
        top_k: int = 3
    ) -> Tuple[List[Dict], str]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: Search query
            doc_types: List of document types to search (e.g., ['fifa_rules', 'var_guidelines'])
            top_k: Number of results per document type
            
        Returns:
            Tuple of (retrieved_chunks, formatted_context)
        """
        if doc_types is None:
            doc_types = ['fifa_rules', 'var_guidelines']
        
        all_results = []
        
        # Retrieve from each document type
        for doc_type in doc_types:
            if doc_type == 'fifa_rules':
                results = self.retriever.retrieve_fifa_rules(query, top_k=top_k)
            elif doc_type == 'var_guidelines':
                results = self.retriever.retrieve_var_guidelines(query, top_k=top_k)
            else:
                results = self.retriever.retrieve(query, index_name=doc_type, top_k=top_k)
            
            all_results.extend(results)
        
        # Sort by relevance score
        all_results.sort(key=lambda x: x['score'])
        
        # Take top results overall
        top_results = all_results[:top_k * len(doc_types)]
        
        # Format context
        formatted_context = self.retriever.format_retrieved_context(top_results)
        
        return top_results, formatted_context
    
    def generate_with_rag(
        self,
        query: str,
        system_prompt: str,
        doc_types: List[str] = None,
        top_k: int = 3,
        include_sources: bool = True
    ) -> Dict:
        """
        Generate response using RAG
        
        Args:
            query: User query
            system_prompt: System instructions
            doc_types: Document types to retrieve from
            top_k: Number of results to retrieve
            include_sources: Whether to include source information
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        # Retrieve relevant context
        retrieved_chunks, formatted_context = self.retrieve_context(
            query, doc_types=doc_types, top_k=top_k
        )
        
        # Generate response with context
        response = self.llm_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=query,
            context=formatted_context
        )
        
        # Calculate confidence score based on retrieval scores
        confidence = self._calculate_confidence(retrieved_chunks)
        
        result = {
            "response": response,
            "confidence": confidence,
            "retrieved_chunks": len(retrieved_chunks),
            "sources": []
        }
        
        # Add source information if requested
        if include_sources:
            result["sources"] = self._format_sources(retrieved_chunks)
        
        return result
    
    def explain_var_decision(
        self,
        decision_description: str,
        match_context: Dict,
        top_k: int = 3
    ) -> Dict:
        """
        Explain VAR decision using RAG
        
        Args:
            decision_description: Description of the VAR decision
            match_context: Match context information
            top_k: Number of relevant rules to retrieve
            
        Returns:
            Dictionary with explanation, rules, and confidence
        """
        # Build query for retrieval
        query = f"VAR decision: {decision_description}"
        
        # Retrieve relevant FIFA rules and VAR guidelines
        retrieved_chunks, formatted_context = self.retrieve_context(
            query,
            doc_types=['fifa_rules', 'var_guidelines'],
            top_k=top_k
        )
        
        # Build system prompt
        system_prompt = """You are an expert football referee and analyst. 
Explain VAR decisions clearly and accurately using the official FIFA Laws of the Game 
and VAR guidelines provided in the context. Be specific about which rules apply and why."""
        
        # Build user message with match context
        match_info = f"""
Match Context:
- Teams: {match_context.get('teams', 'Unknown')}
- Score: {match_context.get('score', 'Unknown')}
- Time: {match_context.get('time', 'Unknown')}

VAR Decision: {decision_description}

Based on the FIFA Laws and VAR guidelines provided, explain:
1. What rule(s) apply to this situation
2. Why the VAR decision was made
3. Whether the decision was correct according to the laws
"""
        
        # Generate explanation
        response = self.llm_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=match_info,
            context=formatted_context
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(retrieved_chunks)
        
        # Extract rules used
        rules_used = self._extract_rules(retrieved_chunks)
        
        return {
            "explanation": response,
            "rules_used": rules_used,
            "retrieved_evidence": self._format_evidence(retrieved_chunks),
            "confidence": confidence,
            "sources": self._format_sources(retrieved_chunks)
        }
    
    def explain_momentum_shift(
        self,
        period_description: str,
        match_context: Dict,
        top_k: int = 2
    ) -> Dict:
        """
        Explain momentum shift with tactical context
        
        Args:
            period_description: Description of the period
            match_context: Match context information
            top_k: Number of relevant contexts to retrieve
            
        Returns:
            Dictionary with explanation and analysis
        """
        # Build query
        query = f"Tactical analysis: {period_description}"
        
        # For momentum, we might not have specific documents yet
        # But we can still use the LLM with match context
        system_prompt = """You are an expert football tactical analyst.
Explain momentum shifts in matches by analyzing tactical changes, player performance,
psychological factors, and key events. Provide detailed tactical insights."""
        
        user_message = f"""
Match Context:
- Teams: {match_context.get('teams', 'Unknown')}
- Score: {match_context.get('score', 'Unknown')}
- Period: {match_context.get('period', 'Unknown')}

Situation: {period_description}

Analyze the momentum shift considering:
1. Tactical adjustments
2. Key events and their impact
3. Psychological factors
4. Statistical indicators
"""
        
        response = self.llm_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=None
        )
        
        return {
            "explanation": response,
            "confidence": 0.75  # Default confidence without retrieval
        }
    
    def _calculate_confidence(self, retrieved_chunks: List[Dict]) -> float:
        """
        Calculate confidence score based on retrieval quality
        
        Args:
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            Confidence score between 0 and 1
        """
        if not retrieved_chunks:
            return 0.5  # Default confidence
        
        # Use inverse of average distance as confidence
        # Lower distance = higher confidence
        avg_score = sum(chunk['score'] for chunk in retrieved_chunks) / len(retrieved_chunks)
        
        # Convert to 0-1 scale (assuming scores are typically 0-2)
        confidence = max(0.0, min(1.0, 1.0 - (avg_score / 2.0)))
        
        return round(confidence, 2)
    
    def _extract_rules(self, retrieved_chunks: List[Dict]) -> List[str]:
        """
        Extract rule references from retrieved chunks
        
        Args:
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            List of rule descriptions
        """
        rules = []
        for chunk in retrieved_chunks:
            source = chunk['metadata'].get('source', 'Unknown')
            text = chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text']
            rules.append(f"{source}: {text}")
        
        return rules
    
    def _format_evidence(self, retrieved_chunks: List[Dict]) -> List[Dict]:
        """
        Format retrieved evidence for display
        
        Args:
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            List of formatted evidence dictionaries
        """
        evidence = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            evidence.append({
                "rank": i,
                "source": chunk['metadata'].get('source', 'Unknown'),
                "text": chunk['text'],
                "relevance": round(1 / (1 + chunk['score']), 2)
            })
        
        return evidence
    
    def _format_sources(self, retrieved_chunks: List[Dict]) -> List[str]:
        """
        Format source citations
        
        Args:
            retrieved_chunks: Retrieved document chunks
            
        Returns:
            List of source citations
        """
        sources = set()
        for chunk in retrieved_chunks:
            source = chunk['metadata'].get('source', 'Unknown')
            sources.add(source)
        
        return sorted(list(sources))


# Made with Bob