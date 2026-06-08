# 🚀 MatchLens AI - Quick Start Guide

## Step-by-Step Instructions to Run the Project

### Prerequisites Check
Before starting, ensure you have:
- ✅ Python 3.9 or higher installed
- ✅ pip (Python package manager)
- ✅ IBM Cloud account (free tier works)
- ✅ Internet connection

---

## 🔧 Step 1: Install Python (if needed)

### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and **check "Add Python to PATH"**
3. Verify installation:
```bash
python --version
```

### macOS/Linux
```bash
# macOS (using Homebrew)
brew install python@3.9

# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.9 python3-pip

# Verify
python3 --version
```

---

## 📦 Step 2: Set Up Virtual Environment

Open your terminal/command prompt in the project directory:

### Windows (PowerShell)
```powershell
# Navigate to project directory
cd "C:\Users\hp\Documents\MatchLens AI"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Windows (Command Prompt)
```cmd
cd "C:\Users\hp\Documents\MatchLens AI"
python -m venv venv
venv\Scripts\activate.bat
```

### macOS/Linux
```bash
cd ~/Documents/MatchLens\ AI
python3 -m venv venv
source venv/bin/activate
```

**You should see `(venv)` at the start of your command prompt**

---

## 📥 Step 3: Install Dependencies

With virtual environment activated:

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- IBM Watson ML SDK
- LangChain
- FAISS
- And all other dependencies

**Installation takes 2-5 minutes depending on your internet speed.**

---

## 🔑 Step 4: Get IBM Cloud Credentials

### 4.1 Create IBM Cloud Account
1. Go to [IBM Cloud](https://cloud.ibm.com)
2. Click "Create an account" (free tier available)
3. Verify your email

### 4.2 Create Watson Machine Learning Service
1. Log in to IBM Cloud Console
2. Click **Catalog** in top menu
3. Search for "Watson Machine Learning"
4. Click on **Watson Machine Learning**
5. Select **Lite** plan (FREE)
6. Click **Create**

### 4.3 Get API Credentials
1. Go to your Watson ML service instance
2. Click **Service credentials** in left menu
3. Click **New credential** button
4. Click **Add**
5. Click **View credentials**
6. Copy these values:
   - `apikey` (looks like: abc123xyz...)
   - `url` (looks like: https://us-south.ml.cloud.ibm.com)

### 4.4 Get Project ID
1. Go to [IBM Watson Studio](https://dataplatform.cloud.ibm.com)
2. Click **Create a project**
3. Choose **Create an empty project**
4. Give it a name (e.g., "MatchLens AI")
5. Click **Create**
6. Click **Manage** tab
7. Copy the **Project ID** (under General)

---

## ⚙️ Step 5: Configure Environment Variables

### 5.1 Create .env file

**Windows:**
```cmd
copy .env.example .env
```

**macOS/Linux:**
```bash
cp .env.example .env
```

### 5.2 Edit .env file

Open `.env` file in any text editor (Notepad, VS Code, etc.) and add your credentials:

```env
# IBM Watson Machine Learning Credentials
IBM_CLOUD_API_KEY=paste_your_api_key_here
IBM_CLOUD_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2
GRANITE_PROJECT_ID=paste_your_project_id_here

# Application Settings (keep as is)
APP_TITLE=MatchLens AI
APP_ICON=⚽
DEBUG_MODE=False

# Vector Database Settings (keep as is)
VECTOR_DB_PATH=./data/vector_db
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Match Data Settings (keep as is)
MATCH_DATA_PATH=./data/matches
```

**Important**: 
- Replace `paste_your_api_key_here` with your actual API key
- Replace `paste_your_project_id_here` with your actual Project ID
- Remove any extra spaces

### 5.3 Save the file

Save and close the `.env` file.

---

## 🎯 Step 6: Run the Application

With virtual environment still activated:

```bash
streamlit run app.py
```

**What happens next:**
1. Streamlit will start the server
2. Your default browser will automatically open
3. The app will load at `http://localhost:8501`
4. You'll see the MatchLens AI interface

**If browser doesn't open automatically:**
- Manually go to: `http://localhost:8501`

---

## 🎮 Step 7: Use the Application

### First Time Setup
On first run, the application will:
1. Create necessary directories
2. Initialize the vector database
3. Load VAR rules
4. Load sample match data

### Navigate Features

**1. Match Momentum Explainer**
- Click "Match Momentum" in sidebar
- Select time period using sliders
- Click "Analyze Momentum"
- View AI explanation and metrics

**2. VAR Decision Explainer**
- Click "VAR Decisions" in sidebar
- Select a VAR decision from dropdown
- Click "Explain Decision"
- Read detailed explanation with rules

**3. Match Story Generator**
- Click "Match Story" in sidebar
- Choose style (dramatic/analytical/casual)
- Choose length (short/medium/long)
- Click "Generate Full Story"
- Download the story if desired

---

## 🛑 Stopping the Application

To stop the application:
1. Go to terminal where Streamlit is running
2. Press `Ctrl + C`
3. Type `deactivate` to exit virtual environment

---

## 🔄 Running Again Later

Next time you want to run the project:

**Windows:**
```cmd
cd "C:\Users\hp\Documents\MatchLens AI"
venv\Scripts\activate
streamlit run app.py
```

**macOS/Linux:**
```bash
cd ~/Documents/MatchLens\ AI
source venv/bin/activate
streamlit run app.py
```

---

## ❗ Troubleshooting

### Problem: "streamlit: command not found"
**Solution:**
```bash
# Make sure virtual environment is activated
# You should see (venv) in your prompt

# Reinstall streamlit
pip install streamlit
```

### Problem: "Import Error: No module named 'streamlit'"
**Solution:**
```bash
# Activate virtual environment first
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Then run
pip install -r requirements.txt
```

### Problem: "Authentication failed" or "Invalid API key"
**Solution:**
1. Check `.env` file has correct API key
2. Ensure no extra spaces in the key
3. Verify key is active in IBM Cloud Console
4. Try regenerating credentials

### Problem: Port 8501 already in use
**Solution:**
```bash
# Use different port
streamlit run app.py --server.port 8502
```

### Problem: Slow AI responses
**Solution:**
- Check internet connection
- Verify IBM Cloud service is active
- Try during off-peak hours
- Check IBM Cloud service status

### Problem: "FAISS installation failed" (Windows)
**Solution:**
```bash
# Install CPU version specifically
pip install faiss-cpu --no-cache-dir
```

---

## 📊 Verify Installation

Test if everything works:

```bash
# Test Python imports
python -c "import streamlit; import ibm_watson_machine_learning; print('✅ All imports successful!')"

# Test configuration
python -c "from src.utils.config import load_config; config = load_config(); print('✅ Configuration loaded!')"
```

---

## 🎓 Learning Resources

### IBM Granite Documentation
- [IBM Watson ML Docs](https://cloud.ibm.com/docs/watson-machine-learning)
- [Granite Models](https://www.ibm.com/products/watsonx-ai/foundation-models)

### Streamlit Documentation
- [Streamlit Docs](https://docs.streamlit.io)
- [Streamlit Gallery](https://streamlit.io/gallery)

### Project Documentation
- `README.md` - Project overview
- `docs/SETUP.md` - Detailed setup
- `docs/ARCHITECTURE.md` - Technical details
- `PROJECT_STRUCTURE.md` - File structure

---

## 💡 Tips for Best Experience

1. **Use Chrome or Firefox** for best Streamlit experience
2. **Keep terminal open** while using the app
3. **Check logs** if something goes wrong (in `logs/` folder)
4. **Start with sample data** before adding custom matches
5. **Try all three features** to see full capabilities

---

## 🆘 Getting Help

If you encounter issues:

1. **Check error messages** in terminal
2. **Review logs** in `logs/app.log`
3. **Enable debug mode** in `.env`: `DEBUG_MODE=True`
4. **Check documentation** in `docs/` folder
5. **Verify IBM Cloud** service is active

---

## ✅ Success Checklist

Before running, ensure:
- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] IBM Cloud account created
- [ ] Watson ML service created
- [ ] API credentials obtained
- [ ] `.env` file configured with credentials
- [ ] Terminal shows `(venv)` prefix

---

## 🎉 You're Ready!

Run this command and enjoy MatchLens AI:

```bash
streamlit run app.py
```

**Welcome to explainable AI for football! ⚽🤖**

---

**Need more help?** Check `docs/SETUP.md` for detailed troubleshooting.