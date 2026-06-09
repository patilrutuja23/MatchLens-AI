# ⚽ MatchLens AI

**Explainable AI for Football Fans** - IBM June Innovation Challenge Submission

MatchLens AI helps football fans understand matches better using IBM Granite AI to provide clear, educational explanations of complex match events, momentum shifts, and tactical decisions.

## 🌐 Live Demo

👉 **Try the App:** https://patilrutuja23-matchlens-ai-app-5g19ip.streamlit.app/

## 🎥 Project Demo

[![MatchLens AI Demo](https://img.youtube.com/vi/h_aB_8qd_5w/maxresdefault.jpg)](https://www.youtube.com/watch?v=h_aB_8qd_5w)

▶️ Watch the full demo: https://www.youtube.com/watch?v=h_aB_8qd_5w

## 🎯 Project Overview

MatchLens AI bridges the gap between casual fans and expert analysis by using explainable AI to break down:
- **Match Momentum**: Why and how momentum shifted during the game
- **VAR Decisions**: Clear explanations of Video Assistant Referee calls with rule references
- **Match Stories**: AI-generated engaging narratives of the entire match

## 🏆 IBM June Innovation Challenge

This project leverages IBM's cutting-edge AI technology to make football more accessible and educational for fans worldwide.

### Key IBM Technologies Used:
- **IBM Granite AI**: Large language model for generating explanations
- **IBM Watson Machine Learning**: Cloud-based AI infrastructure
- **LangChain**: Framework for building AI applications

## ✨ Features

### 1. 📈 Match Momentum Explainer
- Analyzes momentum shifts throughout the match
- Identifies key events that changed the game flow
- Provides AI-powered explanations of tactical changes
- Visual momentum timeline with metrics

### 2. 🎥 VAR Decision Explainer
- Explains Video Assistant Referee decisions
- References official VAR rules
- Breaks down decision factors step-by-step
- Compares similar historical decisions
- Shows VAR statistics for the match

### 3. 📝 Match Story Generator
- Generates engaging match narratives
- Multiple writing styles (dramatic, analytical, casual)
- Customizable story length
- Player highlights and key moments
- Downloadable match reports

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.9+**: Primary programming language
- **Streamlit**: Interactive web application framework
- **IBM Granite API**: AI-powered text generation
- **LangChain**: AI application framework
- **FAISS**: Vector database for semantic search

### AI & ML
- **IBM Watson Machine Learning**: Cloud AI platform
- **Sentence Transformers**: Text embeddings
- **Vector Database**: Context retrieval and similarity search

### Data & Visualization
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **NumPy**: Numerical computations

## 📁 Project Structure

```
MatchLens AI/
│
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
│
├── src/                            # Source code
│   ├── __init__.py
│   │
│   ├── utils/                      # Utility modules
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── granite_client.py      # IBM Granite API client
│   │   └── vector_db.py           # FAISS vector database manager
│   │
│   ├── features/                   # Core feature modules
│   │   ├── __init__.py
│   │   ├── momentum_explainer.py  # Match momentum analysis
│   │   ├── var_explainer.py       # VAR decision explanations
│   │   └── story_generator.py     # Match story generation
│   │
│   └── ui/                         # Streamlit UI components
│       ├── __init__.py
│       ├── sidebar.py             # Navigation sidebar
│       └── pages/                 # Page components
│           ├── __init__.py
│           ├── momentum.py        # Momentum explainer page
│           ├── var_decision.py    # VAR explainer page
│           └── story_generator.py # Story generator page
│
├── data/                           # Data directory
│   ├── matches/                   # Match data files
│   │   └── sample_match.json     # Sample match data
│   └── vector_db/                 # FAISS vector database (generated)
│
├── logs/                           # Application logs (generated)
│
└── docs/                           # Documentation
    ├── SETUP.md                   # Setup instructions
    ├── API_GUIDE.md               # API usage guide
    └── ARCHITECTURE.md            # System architecture
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- IBM Cloud account with Watson Machine Learning access
- IBM Granite API credentials

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd "MatchLens AI"
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Copy the example file
copy .env.example .env

# Edit .env and add your IBM credentials
# IBM_CLOUD_API_KEY=your_api_key_here
# GRANITE_PROJECT_ID=your_project_id_here
```

5. **Run the application**
```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# IBM Watson Machine Learning Credentials
IBM_CLOUD_API_KEY=your_ibm_cloud_api_key
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
GRANITE_PROJECT_ID=your_project_id

# Application Settings
APP_TITLE=MatchLens AI
APP_ICON=⚽
DEBUG_MODE=False

# Vector Database Settings
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Match Data Settings
MATCH_DATA_PATH=./data/matches
```

## 📊 Usage Examples

### Analyzing Match Momentum
1. Navigate to "Match Momentum" in the sidebar
2. Select a time period using the sliders
3. Click "Analyze Momentum"
4. View AI-generated explanations and metrics

### Explaining VAR Decisions
1. Navigate to "VAR Decisions"
2. Select a VAR incident from the dropdown
3. Click "Explain Decision"
4. Read the detailed explanation with rule references

### Generating Match Stories
1. Navigate to "Match Story"
2. Choose your preferred style and length
3. Click "Generate Full Story"
4. Download or share the generated narrative

## 🏗️ Architecture

### System Components

1. **Frontend (Streamlit)**
   - Interactive user interface
   - Real-time updates
   - Responsive design

2. **AI Layer (IBM Granite)**
   - Natural language generation
   - Context-aware explanations
   - Multi-style text generation

3. **Vector Database (FAISS)**
   - Semantic search
   - Context retrieval
   - Rule matching

4. **Data Layer**
   - Match data storage
   - Event tracking
   - Statistics management

## 🤝 Contributing

This is a submission for the IBM June Innovation Challenge. For questions or suggestions, please open an issue.

## 📄 License

This project is created for the IBM June Innovation Challenge.

## 🙏 Acknowledgments

- **IBM** for providing Granite AI and Watson Machine Learning platform
- **Streamlit** for the excellent web framework
- **LangChain** for AI application tools
- **FAISS** for efficient vector search

## 📧 Contact

For questions about this project, please contact the development team.

---

**Built with ❤️ for football fans worldwide**

*Powered by IBM Granite AI*
