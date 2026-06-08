# MatchLens AI - Complete Project Structure

## 📁 Directory Tree

```
MatchLens AI/
│
├── 📄 app.py                          # Main Streamlit application entry point
├── 📄 requirements.txt                # Python dependencies
├── 📄 .env.example                    # Environment variables template
├── 📄 .gitignore                      # Git ignore rules
├── 📄 README.md                       # Project documentation
├── 📄 PROJECT_STRUCTURE.md            # This file - complete structure overview
│
├── 📁 src/                            # Source code directory
│   ├── 📄 __init__.py                # Package initialization
│   │
│   ├── 📁 utils/                      # Utility modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py              # Configuration management
│   │   ├── 📄 granite_client.py      # IBM Granite API client
│   │   └── 📄 vector_db.py           # FAISS vector database manager
│   │
│   ├── 📁 features/                   # Core feature modules
│   │   ├── 📄 __init__.py
│   │   ├── 📄 momentum_explainer.py  # Match momentum analysis
│   │   ├── 📄 var_explainer.py       # VAR decision explanations
│   │   └── 📄 story_generator.py     # Match story generation
│   │
│   └── 📁 ui/                         # Streamlit UI components
│       ├── 📄 __init__.py
│       ├── 📄 sidebar.py             # Navigation sidebar
│       └── 📁 pages/                 # Page components
│           ├── 📄 __init__.py
│           ├── 📄 momentum.py        # Momentum explainer page
│           ├── 📄 var_decision.py    # VAR explainer page
│           └── 📄 story_generator.py # Story generator page
│
├── 📁 data/                           # Data directory
│   ├── 📁 matches/                   # Match data files
│   │   └── 📄 sample_match.json     # Sample match data
│   └── 📁 vector_db/                 # FAISS vector database (auto-generated)
│
├── 📁 docs/                           # Documentation
│   ├── 📄 SETUP.md                   # Setup instructions
│   ├── 📄 ARCHITECTURE.md            # System architecture
│   └── 📄 API_GUIDE.md               # API usage guide
│
└── 📁 logs/                           # Application logs (auto-generated)
```

## 📋 File Descriptions

### Root Level Files

#### `app.py`
**Purpose**: Main application entry point
**Key Functions**:
- Initialize Streamlit configuration
- Load application settings
- Route to appropriate pages
- Manage application state

**Dependencies**:
- Streamlit
- UI components from `src/ui/`
- Configuration from `src/utils/config.py`

---

#### `requirements.txt`
**Purpose**: Python package dependencies
**Key Packages**:
- `streamlit==1.31.0` - Web framework
- `ibm-watson-machine-learning==1.0.335` - IBM Granite API
- `langchain==0.1.10` - AI framework
- `faiss-cpu==1.7.4` - Vector database
- `sentence-transformers==2.3.1` - Text embeddings
- `plotly==5.18.0` - Visualizations
- `pandas==2.2.0` - Data manipulation

---

#### `.env.example`
**Purpose**: Environment variables template
**Variables**:
- `IBM_CLOUD_API_KEY` - IBM Cloud authentication
- `IBM_CLOUD_URL` - IBM service endpoint
- `GRANITE_MODEL_ID` - AI model identifier
- `GRANITE_PROJECT_ID` - Project identifier
- `VECTOR_DB_PATH` - Database storage path
- `EMBEDDING_MODEL` - Embedding model name

---

#### `.gitignore`
**Purpose**: Exclude files from version control
**Excludes**:
- Environment files (`.env`)
- Python cache (`__pycache__/`)
- Virtual environments (`venv/`)
- Generated data (`data/vector_db/`)
- Logs (`*.log`)

---

### Source Code (`src/`)

#### `src/utils/config.py`
**Purpose**: Configuration management
**Classes**:
- `Settings` - Pydantic settings model
**Functions**:
- `load_config()` - Load environment configuration
- `get_project_root()` - Get project root directory
- `ensure_directories()` - Create required directories

**Usage**:
```python
from src.utils.config import load_config
config = load_config()
```

---

#### `src/utils/granite_client.py`
**Purpose**: IBM Granite API client
**Classes**:
- `GraniteClient` - API wrapper
**Methods**:
- `generate()` - Basic text generation
- `generate_with_context()` - Context-aware generation
- `explain_decision()` - Decision explanation

**Features**:
- Automatic credential management
- Configurable generation parameters
- Error handling and retries
- Prompt engineering utilities

**Usage**:
```python
from src.utils.granite_client import GraniteClient
client = GraniteClient()
response = client.generate("Your prompt")
```

---

#### `src/utils/vector_db.py`
**Purpose**: FAISS vector database manager
**Classes**:
- `VectorDatabase` - Database wrapper
**Methods**:
- `add_documents()` - Store documents
- `search()` - Semantic search
- `clear()` - Reset database
- `get_stats()` - Database statistics

**Features**:
- Automatic embedding generation
- Persistent storage
- Similarity search
- Metadata management

**Usage**:
```python
from src.utils.vector_db import VectorDatabase
db = VectorDatabase()
db.add_documents(["Document 1", "Document 2"])
results = db.search("query", k=5)
```

---

#### `src/features/momentum_explainer.py`
**Purpose**: Match momentum analysis
**Classes**:
- `MomentumExplainer` - Momentum analyzer
**Methods**:
- `analyze_momentum_shift()` - Analyze specific period
- `get_momentum_timeline()` - Full match timeline
- `_calculate_momentum_metrics()` - Compute metrics
- `_identify_key_events()` - Find important events

**Features**:
- Time-period analysis
- Event classification
- Momentum scoring (-100 to +100)
- AI-powered explanations
- Key event identification

**Output**:
```python
{
    "explanation": "AI-generated explanation",
    "metrics": {
        "momentum_score": 45,
        "attacking_events": 12,
        "defensive_events": 8
    },
    "key_events": [...]
}
```

---

#### `src/features/var_explainer.py`
**Purpose**: VAR decision explanations
**Classes**:
- `VARExplainer` - VAR analyzer
**Methods**:
- `explain_var_decision()` - Explain decision
- `get_var_statistics()` - Match statistics
- `compare_similar_decisions()` - Historical comparison
- `_analyze_decision_factors()` - Factor analysis

**Features**:
- Rule-based explanations
- Decision factor analysis
- Historical comparisons
- Statistics tracking
- Multi-angle analysis

**Output**:
```python
{
    "explanation": "Detailed explanation",
    "relevant_rules": ["Rule 1", "Rule 2"],
    "decision_factors": {...},
    "final_decision": "Penalty awarded"
}
```

---

#### `src/features/story_generator.py`
**Purpose**: Match story generation
**Classes**:
- `StoryGenerator` - Story generator
**Methods**:
- `generate_match_story()` - Full narrative
- `generate_quick_summary()` - Brief summary
- `_generate_title()` - Create headline
- `_generate_player_highlights()` - Player analysis

**Features**:
- Multiple writing styles (dramatic, analytical, casual)
- Customizable length (short, medium, long)
- Player highlights
- Key moments timeline
- Downloadable reports

**Output**:
```python
{
    "full_story": "Complete narrative",
    "sections": {
        "title": "...",
        "introduction": "...",
        "first_half": "...",
        "second_half": "...",
        "conclusion": "..."
    },
    "word_count": 850
}
```

---

### UI Components (`src/ui/`)

#### `src/ui/sidebar.py`
**Purpose**: Navigation sidebar
**Functions**:
- `render_sidebar()` - Render sidebar UI
**Features**:
- Page navigation
- Match selection
- AI settings
- Application info

---

#### `src/ui/pages/momentum.py`
**Purpose**: Momentum explainer page
**Functions**:
- `render_momentum_page()` - Main page renderer
**Features**:
- Time period selection
- Momentum analysis
- Metrics visualization
- Full timeline generation

---

#### `src/ui/pages/var_decision.py`
**Purpose**: VAR explainer page
**Functions**:
- `render_var_page()` - Main page renderer
**Features**:
- Decision selection
- Rule references
- Factor analysis
- Statistics display

---

#### `src/ui/pages/story_generator.py`
**Purpose**: Story generator page
**Functions**:
- `render_story_page()` - Main page renderer
**Features**:
- Style selection
- Length customization
- Quick summary
- Full story generation
- Download functionality

---

### Data Files

#### `data/matches/sample_match.json`
**Purpose**: Sample match data
**Structure**:
```json
{
  "match_id": "sample_001",
  "home_team": "Team A",
  "away_team": "Team B",
  "final_score": "3-2",
  "events": [...],
  "top_performers": [...]
}
```

---

### Documentation (`docs/`)

#### `docs/SETUP.md`
**Purpose**: Installation and setup guide
**Sections**:
- Prerequisites
- IBM Cloud setup
- Local installation
- Configuration
- Troubleshooting

---

#### `docs/ARCHITECTURE.md`
**Purpose**: System architecture documentation
**Sections**:
- System overview
- Component details
- Data flow
- AI integration
- Security

---

#### `docs/API_GUIDE.md`
**Purpose**: API usage documentation
**Sections**:
- Granite Client API
- Vector Database API
- Feature APIs
- Examples
- Best practices

---

## 🔄 Data Flow

### 1. Application Startup
```
app.py
  ↓
Load config (src/utils/config.py)
  ↓
Initialize UI (src/ui/sidebar.py)
  ↓
Render selected page
```

### 2. Momentum Analysis
```
User selects time period
  ↓
momentum.py (UI)
  ↓
MomentumExplainer.analyze_momentum_shift()
  ↓
VectorDatabase.search() (context)
  ↓
GraniteClient.generate_with_context()
  ↓
Display results
```

### 3. VAR Explanation
```
User selects VAR decision
  ↓
var_decision.py (UI)
  ↓
VARExplainer.explain_var_decision()
  ↓
VectorDatabase.search() (rules)
  ↓
GraniteClient.generate_with_context()
  ↓
Display explanation
```

### 4. Story Generation
```
User selects style/length
  ↓
story_generator.py (UI)
  ↓
StoryGenerator.generate_match_story()
  ↓
Multiple GraniteClient calls (sections)
  ↓
Combine sections
  ↓
Display and download
```

---

## 🔧 Configuration Flow

```
.env file
  ↓
src/utils/config.py (Settings class)
  ↓
load_config()
  ↓
Used by:
  - GraniteClient
  - VectorDatabase
  - Feature modules
```

---

## 📊 Key Technologies

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | Streamlit | Web UI |
| AI Model | IBM Granite | Text generation |
| Vector DB | FAISS | Semantic search |
| Embeddings | Sentence Transformers | Text embeddings |
| Visualization | Plotly | Charts |
| Data | Pandas | Data manipulation |

---

## 🚀 Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run application**:
   ```bash
   streamlit run app.py
   ```

---

## 📝 Development Guidelines

### Adding a New Feature

1. Create feature module in `src/features/`
2. Create UI page in `src/ui/pages/`
3. Update sidebar navigation in `src/ui/sidebar.py`
4. Add route in `app.py`
5. Update documentation

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Handle errors gracefully
- Log important events

---

**Last Updated**: 2026-06-08
**Version**: 1.0.0