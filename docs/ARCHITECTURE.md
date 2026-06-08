# MatchLens AI - System Architecture

Technical architecture and design documentation for MatchLens AI.

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Component Details](#component-details)
4. [Data Flow](#data-flow)
5. [AI Integration](#ai-integration)
6. [Database Design](#database-design)
7. [Security](#security)

## Overview

MatchLens AI is a three-tier application that uses IBM Granite AI to provide explainable insights into football matches.

### Architecture Principles
- **Modularity**: Separate concerns into distinct modules
- **Scalability**: Design for future growth
- **Maintainability**: Clean, documented code
- **Explainability**: Transparent AI decision-making

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│                      (Streamlit UI)                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Momentum   │  │     VAR      │  │    Story     │     │
│  │     Page     │  │   Decision   │  │  Generator   │     │
│  │              │  │     Page     │  │     Page     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Momentum   │  │     VAR      │  │    Story     │     │
│  │  Explainer   │  │  Explainer   │  │  Generator   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Integration Layer                       │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Granite    │  │    Vector    │  │    Config    │     │
│  │    Client    │  │   Database   │  │   Manager    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       External Services                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  IBM Granite │  │    FAISS     │  │  Match Data  │     │
│  │      API     │  │   Storage    │  │    Files     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Presentation Layer (UI)

#### Streamlit Application (`app.py`)
- **Purpose**: Main entry point and orchestration
- **Responsibilities**:
  - Initialize application
  - Route to appropriate pages
  - Manage session state
  - Handle user interactions

#### Sidebar Component (`src/ui/sidebar.py`)
- **Purpose**: Navigation and settings
- **Features**:
  - Page navigation
  - Match selection
  - AI settings configuration
  - Application information

#### Page Components (`src/ui/pages/`)
- **Momentum Page**: Interactive momentum analysis
- **VAR Page**: VAR decision explanations
- **Story Page**: Match narrative generation

### 2. Business Logic Layer

#### Momentum Explainer (`src/features/momentum_explainer.py`)
```python
class MomentumExplainer:
    - analyze_momentum_shift()    # Analyze specific period
    - get_momentum_timeline()     # Full match timeline
    - _calculate_momentum_metrics() # Compute metrics
    - _identify_key_events()      # Find important events
```

**Key Features**:
- Time-period analysis
- Event classification
- Momentum scoring (-100 to +100)
- AI-powered explanations

#### VAR Explainer (`src/features/var_explainer.py`)
```python
class VARExplainer:
    - explain_var_decision()      # Explain specific decision
    - get_var_statistics()        # Match VAR stats
    - compare_similar_decisions() # Historical comparison
    - _analyze_decision_factors() # Factor analysis
```

**Key Features**:
- Rule-based explanations
- Decision factor analysis
- Historical comparisons
- Statistics tracking

#### Story Generator (`src/features/story_generator.py`)
```python
class StoryGenerator:
    - generate_match_story()      # Full match narrative
    - generate_quick_summary()    # Brief summary
    - _generate_title()           # Create headline
    - _generate_player_highlights() # Player analysis
```

**Key Features**:
- Multiple writing styles
- Customizable length
- Player highlights
- Downloadable reports

### 3. Integration Layer

#### Granite Client (`src/utils/granite_client.py`)
```python
class GraniteClient:
    - generate()                  # Basic text generation
    - generate_with_context()     # Context-aware generation
    - explain_decision()          # Decision explanation
```

**Responsibilities**:
- IBM Granite API communication
- Prompt engineering
- Response parsing
- Error handling

**Configuration**:
- Model: `ibm/granite-13b-chat-v2`
- Max tokens: 500 (configurable)
- Temperature: 0.7 (configurable)

#### Vector Database (`src/utils/vector_db.py`)
```python
class VectorDatabase:
    - add_documents()             # Store documents
    - search()                    # Semantic search
    - clear()                     # Reset database
    - get_stats()                 # Database statistics
```

**Technology**: FAISS (Facebook AI Similarity Search)
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Index Type**: IndexFlatL2 (L2 distance)
- **Storage**: Persistent file-based

#### Config Manager (`src/utils/config.py`)
```python
class Settings:
    - IBM credentials
    - Application settings
    - Database paths
    - Model configurations
```

## Data Flow

### 1. Match Momentum Analysis Flow
```
User selects time period
        ↓
Filter events for period
        ↓
Calculate momentum metrics
        ↓
Search vector DB for similar patterns
        ↓
Generate AI explanation with context
        ↓
Display results with visualizations
```

### 2. VAR Decision Explanation Flow
```
User selects VAR decision
        ↓
Load decision details
        ↓
Search vector DB for relevant rules
        ↓
Analyze decision factors
        ↓
Generate AI explanation with rules
        ↓
Display explanation and factors
```

### 3. Story Generation Flow
```
User selects style and length
        ↓
Extract key moments from match
        ↓
Generate story sections (title, intro, halves, conclusion)
        ↓
Generate player highlights
        ↓
Combine sections into full story
        ↓
Display and offer download
```

## AI Integration

### IBM Granite API Integration

#### Authentication
```python
credentials = {
    "url": IBM_CLOUD_URL,
    "apikey": IBM_CLOUD_API_KEY
}
```

#### Model Configuration
```python
params = {
    "decoding_method": "greedy",
    "max_new_tokens": 500,
    "temperature": 0.7,
    "top_k": 50,
    "top_p": 1
}
```

#### Prompt Engineering

**System Prompt Structure**:
```
System: [Role and instructions]
Context: [Relevant information]
User: [Specific query]
Assistant: [AI response]
```

**Example**:
```python
system_prompt = "You are an expert football analyst..."
context = "Match: Team A vs Team B\nScore: 2-1\n..."
user_message = "Explain the momentum shift..."
```

### Vector Database Integration

#### Embedding Generation
- Model: Sentence Transformers
- Dimension: 384
- Method: Mean pooling

#### Similarity Search
- Algorithm: L2 distance
- Top-K retrieval
- Threshold filtering

## Database Design

### Match Data Schema
```json
{
  "match_id": "string",
  "home_team": "string",
  "away_team": "string",
  "final_score": "string",
  "events": [
    {
      "time": "number",
      "type": "string",
      "team": "string",
      "player": "string",
      "description": "string"
    }
  ],
  "top_performers": [...]
}
```

### Vector Database Schema
```python
{
    "documents": List[str],      # Text documents
    "metadata": List[Dict],      # Associated metadata
    "embeddings": np.ndarray     # Vector embeddings
}
```

## Security

### API Key Management
- Environment variables (`.env`)
- Never committed to version control
- Secure credential storage

### Data Privacy
- No personal data collection
- Match data stored locally
- No external data transmission (except IBM API)

### Error Handling
```python
try:
    response = granite_client.generate(prompt)
except Exception as e:
    logger.error(f"Generation failed: {e}")
    return fallback_response
```

## Performance Considerations

### Optimization Strategies
1. **Caching**: Session state for repeated queries
2. **Lazy Loading**: Load data only when needed
3. **Batch Processing**: Process multiple events together
4. **Vector DB**: Fast semantic search with FAISS

### Scalability
- Stateless design for horizontal scaling
- Efficient vector operations
- Configurable batch sizes
- Resource pooling

## Future Enhancements

### Planned Features
1. Real-time match analysis
2. Multi-language support
3. Custom model fine-tuning
4. Advanced visualizations
5. Mobile application

### Technical Improvements
1. Distributed vector database
2. Model caching
3. Response streaming
4. A/B testing framework

## Monitoring and Logging

### Application Logs
- Location: `logs/app.log`
- Level: INFO (configurable)
- Rotation: Daily

### Metrics Tracked
- API response times
- Error rates
- User interactions
- Feature usage

---

**Last Updated**: 2026-06-08
**Version**: 1.0.0