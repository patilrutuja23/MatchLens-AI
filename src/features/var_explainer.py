"""
VAR Decision Explainer with RAG
Explains Video Assistant Referee decisions using AI with FIFA rules retrieval
"""

from typing import Dict, List, Optional
from src.utils.granite_client import GraniteClient
from src.utils.vector_db import VectorDatabase
from src.utils.rag_chain import RAGChain

class VARExplainer:
    """Explains VAR decisions using AI with RAG-enhanced context"""
    
    def __init__(self, use_rag: bool = True):
        """
        Initialize VAR explainer
        
        Args:
            use_rag: Whether to use RAG for enhanced explanations
        """
        self.granite_client = GraniteClient()
        self.vector_db = VectorDatabase()
        self.use_rag = use_rag
        
        # Initialize RAG chain if enabled
        if self.use_rag:
            try:
                self.rag_chain = RAGChain()
                print("✅ VAR Explainer initialized with RAG")
            except Exception as e:
                print(f"⚠️  RAG initialization failed: {e}")
                print("⚠️  Falling back to basic mode")
                self.use_rag = False
                self.rag_chain = None
        else:
            self.rag_chain = None
            print("✅ VAR Explainer initialized (basic mode)")
        
        # Load basic VAR rules as fallback
        self._load_var_rules()
    
    def _load_var_rules(self):
        """Load basic VAR rules into vector database (fallback)"""
        var_rules = [
            "VAR can review goals and offenses leading up to a goal",
            "VAR can review penalty decisions and offenses in the penalty area",
            "VAR can review direct red card incidents",
            "VAR can review mistaken identity when a referee cautions or sends off the wrong player",
            "Offside is checked for goals and penalty decisions",
            "VAR uses multiple camera angles to make accurate decisions",
            "The on-field referee makes the final decision after VAR review",
            "Clear and obvious errors are required for VAR intervention",
            "Handball in the buildup to a goal is always reviewed",
            "Violent conduct and serious foul play are reviewable by VAR"
        ]
        
        # Check if rules already loaded
        stats = self.vector_db.get_stats()
        if stats["total_documents"] < len(var_rules):
            metadata = [{"type": "var_rule", "rule_id": i} for i in range(len(var_rules))]
            self.vector_db.add_documents(var_rules, metadata)
    
    def explain_var_decision(
        self,
        decision_type: str,
        match_context: Dict,
        incident_details: Dict
    ) -> Dict:
        """
        Explain a VAR decision with RAG-enhanced context
        
        Args:
            decision_type: Type of VAR decision (goal, penalty, red_card, offside)
            match_context: Match context information
            incident_details: Details of the specific incident
            
        Returns:
            Comprehensive explanation with relevant rules, evidence, and confidence
        """
        if self.use_rag and self.rag_chain:
            return self._explain_with_rag(decision_type, match_context, incident_details)
        else:
            return self._explain_basic(decision_type, match_context, incident_details)
    
    def _explain_with_rag(
        self,
        decision_type: str,
        match_context: Dict,
        incident_details: Dict
    ) -> Dict:
        """Explain VAR decision using RAG with FIFA rules retrieval"""
        
        # Safety check: ensure rag_chain is available
        if not self.rag_chain:
            return self._explain_basic(decision_type, match_context, incident_details)
        
        # Build detailed description for retrieval
        description = incident_details.get('description', '')
        time = incident_details.get('time', 'Unknown')
        
        decision_description = f"{decision_type} decision at {time}: {description}"
        
        # Use RAG chain to get explanation with retrieved FIFA rules
        rag_result = self.rag_chain.explain_var_decision(
            decision_description=decision_description,
            match_context=match_context,
            top_k=3
        )
        
        # Analyze decision factors
        factors = self._analyze_decision_factors(decision_type, incident_details)
        
        # Build comprehensive result
        result = {
            "explanation": rag_result["explanation"],
            "decision_type": decision_type,
            "rules_used": rag_result["rules_used"],
            "retrieved_evidence": rag_result["retrieved_evidence"],
            "confidence_score": rag_result["confidence"],
            "decision_factors": factors,
            "final_decision": incident_details.get("final_decision", "Unknown"),
            "review_duration": incident_details.get("review_duration", "Unknown"),
            "sources": rag_result["sources"],
            "rag_enabled": True
        }
        
        return result
    
    def _explain_basic(
        self,
        decision_type: str,
        match_context: Dict,
        incident_details: Dict
    ) -> Dict:
        """Explain VAR decision using basic mode (fallback)"""
        
        # Search for relevant VAR rules from basic database
        query = f"{decision_type} {incident_details.get('description', '')}"
        relevant_rules = self.vector_db.search(query, k=3)
        
        # Generate explanation
        explanation = self._generate_var_explanation(
            decision_type,
            match_context,
            incident_details,
            relevant_rules
        )
        
        # Analyze decision factors
        factors = self._analyze_decision_factors(decision_type, incident_details)
        
        return {
            "explanation": explanation,
            "decision_type": decision_type,
            "relevant_rules": [rule[0] for rule in relevant_rules],
            "decision_factors": factors,
            "final_decision": incident_details.get("final_decision", "Unknown"),
            "review_duration": incident_details.get("review_duration", "Unknown"),
            "confidence_score": 0.7,  # Default confidence
            "rag_enabled": False
        }
    
    def _generate_var_explanation(
        self,
        decision_type: str,
        match_context: Dict,
        incident_details: Dict,
        relevant_rules: List
    ) -> str:
        """Generate AI explanation for VAR decision (basic mode)"""
        system_prompt = f"""You are an expert football referee and analyst. 
Explain this VAR {decision_type} decision clearly and educationally. 
Reference the relevant rules and explain why the decision was made. 
Help fans understand the reasoning behind the decision."""
        
        # Build context
        context_parts = [
            f"Match: {match_context.get('home_team', 'Home')} vs {match_context.get('away_team', 'Away')}",
            f"Score: {match_context.get('score', '0-0')}",
            f"Time: {incident_details.get('time', 'Unknown')}",
            f"Incident: {incident_details.get('description', 'Unknown')}",
            f"Initial Decision: {incident_details.get('initial_decision', 'Unknown')}",
            f"VAR Review: {incident_details.get('var_review', 'Unknown')}",
            f"Final Decision: {incident_details.get('final_decision', 'Unknown')}"
        ]
        
        # Add relevant rules
        if relevant_rules:
            context_parts.append("\nRelevant VAR Rules:")
            for rule, meta, dist in relevant_rules:
                context_parts.append(f"- {rule}")
        
        context = "\n".join(context_parts)
        
        user_message = f"Explain this VAR {decision_type} decision step by step."
        
        return self.granite_client.generate_with_context(
            system_prompt=system_prompt,
            user_message=user_message,
            context=context
        )
    
    def _analyze_decision_factors(
        self,
        decision_type: str,
        incident_details: Dict
    ) -> Dict:
        """Analyze factors that influenced the VAR decision"""
        factors = {
            "decision_type": decision_type,
            "clear_and_obvious": False,
            "multiple_angles_used": False,
            "key_considerations": []
        }
        
        # Analyze based on decision type
        if decision_type.lower() == "offside":
            factors["key_considerations"].extend([
                "Player position relative to second-last defender",
                "Moment ball was played",
                "Active involvement in play"
            ])
            factors["multiple_angles_used"] = True
        
        elif decision_type.lower() == "penalty":
            factors["key_considerations"].extend([
                "Contact location (inside penalty area)",
                "Nature of contact (foul or fair challenge)",
                "Impact on attacking player"
            ])
        
        elif decision_type.lower() == "red_card":
            factors["key_considerations"].extend([
                "Severity of the offense",
                "Endangering opponent safety",
                "Denial of obvious goal-scoring opportunity"
            ])
        
        elif decision_type.lower() == "goal":
            factors["key_considerations"].extend([
                "Offside in buildup",
                "Fouls in buildup",
                "Handball by attacking team"
            ])
        
        # Check if decision was overturned
        initial = incident_details.get("initial_decision", "").lower()
        final = incident_details.get("final_decision", "").lower()
        
        if initial != final:
            factors["clear_and_obvious"] = True
        
        return factors
    
    def compare_similar_decisions(
        self,
        current_decision: Dict,
        match_history: List[Dict]
    ) -> List[Dict]:
        """
        Compare current VAR decision with similar historical decisions
        
        Args:
            current_decision: Current VAR decision details
            match_history: Historical match data
            
        Returns:
            List of similar decisions with comparisons
        """
        decision_type = current_decision.get("decision_type", "")
        description = current_decision.get("description", "")
        
        # Search for similar decisions
        query = f"{decision_type} {description}"
        similar = self.vector_db.search(query, k=5)
        
        comparisons = []
        for doc, meta, distance in similar:
            if meta.get("type") != "var_rule":  # Exclude rules
                comparisons.append({
                    "description": doc,
                    "metadata": meta,
                    "similarity_score": 1 / (1 + distance)  # Convert distance to similarity
                })
        
        return comparisons
    
    def get_var_statistics(self, match_data: Dict) -> Dict:
        """
        Get VAR usage statistics for a match
        
        Args:
            match_data: Complete match data
            
        Returns:
            VAR statistics
        """
        var_events = [
            event for event in match_data.get("events", [])
            if event.get("type", "").lower() == "var"
        ]
        
        stats = {
            "total_var_reviews": len(var_events),
            "decisions_overturned": 0,
            "decisions_upheld": 0,
            "average_review_time": 0,
            "by_type": {}
        }
        
        total_time = 0
        for event in var_events:
            decision_type = event.get("decision_type", "other")
            
            # Count by type
            stats["by_type"][decision_type] = stats["by_type"].get(decision_type, 0) + 1
            
            # Check if overturned
            if event.get("initial_decision") != event.get("final_decision"):
                stats["decisions_overturned"] += 1
            else:
                stats["decisions_upheld"] += 1
            
            # Add review time
            review_time = event.get("review_duration", 0)
            if isinstance(review_time, (int, float)):
                total_time += review_time
        
        if len(var_events) > 0:
            stats["average_review_time"] = total_time / len(var_events)
        
        return stats

# Made with Bob
