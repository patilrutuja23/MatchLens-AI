# MatchLens AI - Setup Guide

Complete setup instructions for MatchLens AI application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [IBM Cloud Setup](#ibm-cloud-setup)
3. [Local Installation](#local-installation)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux
- **Python**: Version 3.9 or higher
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: At least 2GB free space

### Required Accounts
- IBM Cloud account (free tier available)
- Git (for cloning the repository)

## IBM Cloud Setup

### Step 1: Create IBM Cloud Account
1. Visit [IBM Cloud](https://cloud.ibm.com)
2. Sign up for a free account
3. Verify your email address

### Step 2: Create Watson Machine Learning Service
1. Log in to IBM Cloud Console
2. Navigate to **Catalog** > **AI / Machine Learning**
3. Select **Watson Machine Learning**
4. Choose the **Lite** (free) plan
5. Click **Create**

### Step 3: Get API Credentials
1. Go to your Watson ML service instance
2. Click on **Service credentials** in the left menu
3. Click **New credential**
4. Copy the following values:
   - `apikey`
   - `url`

### Step 4: Create a Project
1. Navigate to **Watson Studio**
2. Create a new project
3. Copy the **Project ID** from project settings

## Local Installation

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "MatchLens AI"
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- IBM Watson ML SDK
- LangChain (AI framework)
- FAISS (vector database)
- All other required packages

### Step 4: Verify Installation
```bash
python -c "import streamlit; import ibm_watson_machine_learning; print('Installation successful!')"
```

## Configuration

### Step 1: Create Environment File
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

### Step 2: Edit Configuration
Open `.env` file and add your credentials:

```env
# IBM Watson Machine Learning Credentials
IBM_CLOUD_API_KEY=your_actual_api_key_here
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
GRANITE_PROJECT_ID=your_actual_project_id_here

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

### Step 3: Create Required Directories
The application will create these automatically, but you can create them manually:

```bash
mkdir -p data/vector_db
mkdir -p data/matches
mkdir -p logs
```

## Running the Application

### Start the Application
```bash
streamlit run app.py
```

### Access the Application
The application will automatically open in your default browser at:
```
http://localhost:8501
```

If it doesn't open automatically, manually navigate to the URL above.

### First Run
On first run, the application will:
1. Initialize the vector database
2. Load VAR rules
3. Create necessary directories
4. Load sample match data

## Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError: No module named 'streamlit'`

**Solution**:
```bash
# Ensure virtual environment is activated
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. IBM API Authentication Error
**Problem**: `Authentication failed`

**Solution**:
- Verify your API key in `.env` file
- Ensure no extra spaces in the API key
- Check that your IBM Cloud service is active
- Verify the project ID is correct

#### 3. Port Already in Use
**Problem**: `Port 8501 is already in use`

**Solution**:
```bash
# Use a different port
streamlit run app.py --server.port 8502
```

#### 4. FAISS Installation Issues
**Problem**: FAISS fails to install on Windows

**Solution**:
```bash
# Use CPU version
pip install faiss-cpu
```

#### 5. Slow Response Times
**Problem**: AI responses are very slow

**Solution**:
- Check your internet connection
- Verify IBM Cloud service status
- Consider using a different region in IBM_CLOUD_URL
- Reduce the max_tokens parameter in config

### Getting Help

If you encounter issues not covered here:

1. Check the [IBM Watson ML Documentation](https://cloud.ibm.com/docs/watson-machine-learning)
2. Review Streamlit documentation at [docs.streamlit.io](https://docs.streamlit.io)
3. Check application logs in the `logs/` directory
4. Enable debug mode in `.env`: `DEBUG_MODE=True`

## Development Mode

### Enable Debug Logging
```env
DEBUG_MODE=True
```

### Run with Auto-Reload
Streamlit automatically reloads when you save changes to Python files.

### View Logs
```bash
# Windows
type logs\app.log

# macOS/Linux
tail -f logs/app.log
```

## Testing

### Test IBM Connection
```python
python -c "
from src.utils.granite_client import GraniteClient
client = GraniteClient()
print('IBM Granite connection successful!')
"
```

### Test Vector Database
```python
python -c "
from src.utils.vector_db import VectorDatabase
db = VectorDatabase()
print(f'Vector DB initialized: {db.get_stats()}')
"
```

## Next Steps

After successful setup:
1. Explore the sample match data in `data/matches/sample_match.json`
2. Try each feature (Momentum, VAR, Story Generator)
3. Review the [API Guide](API_GUIDE.md) for customization
4. Check [Architecture](ARCHITECTURE.md) to understand the system

## Updates

To update the application:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

**Need Help?** Check the main [README.md](../README.md) or open an issue.