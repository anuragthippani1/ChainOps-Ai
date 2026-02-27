# ChainOps AI Setup Guide

## 🚀 Quick Start (Recommended)

### Option 1: One-Click Start (Windows)

```bash
# Double-click start.bat or run:
start.bat
```

### Option 2: One-Click Start (Mac/Linux)

```bash
# Make executable and run:
chmod +x start.sh
./start.sh
```

### Option 3: Manual Start

```bash
# Install all dependencies
npm run install-all

# Start both frontend and backend
npm run dev
```

## 📋 Prerequisites

- **Node.js 16+** and npm
- **Python 3.8+** and pip
- **MongoDB** (optional - app works without it)

### Installing Prerequisites

#### Windows

1. Download Node.js from https://nodejs.org/
2. Download Python from https://python.org/
3. Install MongoDB Community Edition from https://mongodb.com/try/download/community

#### Mac

```bash
# Using Homebrew
brew install node python mongodb-community
```

#### Linux (Ubuntu/Debian)

```bash
# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python
sudo apt-get install python3 python3-pip

# MongoDB
wget -qO - https://www.mongodb.org/static/server/public-key.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

## 🔧 Configuration

### Environment Variables (Optional)

The app works with sample data by default. For live data, create `backend/.env`:

```env
# OpenAI API Key (for enhanced responses)
OPENAI_API_KEY=your-openai-key-here

# News API Keys (for live political risk data)
NEWSDATA_API_KEY=your-newsdata-key-here
GNEWS_API_KEY=your-gnews-key-here

# MongoDB (optional - uses file fallback)
MONGODB_URI=mongodb://localhost:27017/chainops_ai
```

### Getting API Keys (Free)

1. **OpenAI API Key** (Optional)

   - Visit https://platform.openai.com/api-keys
   - Create account and generate API key
   - Free tier includes $5 credit

2. **NewsData.io API Key** (Optional)

   - Visit https://newsdata.io/register
   - Sign up for free account
   - Get API key from dashboard

3. **GNews API Key** (Optional)
   - Visit https://gnews.io/register
   - Sign up for free account
   - Get API key from dashboard

## 🏃‍♂️ Running the Application

### Start Backend Only

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Start Frontend Only

```bash
cd frontend
npm start
```

### Start Both (Recommended)

```bash
# From project root
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🧪 Testing

### Test Backend

```bash
python test_app.py
```

### Test Frontend

1. Open http://localhost:3000
2. Check if dashboard loads
3. Try chat functionality
4. Navigate between pages

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Kill processes on ports 3000 and 8000
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:3000 | xargs kill -9
lsof -ti:8000 | xargs kill -9
```

#### 2. Python Dependencies Issues

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

#### 3. Node Dependencies Issues

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### 4. MongoDB Connection Issues

- The app works without MongoDB (uses file storage)
- To use MongoDB: ensure it's running on port 27017
- Check MongoDB status: `mongod --version`

#### 5. CORS Issues

- Make sure backend is running on port 8000
- Check browser console for CORS errors
- Verify frontend is on port 3000

### Logs and Debugging

#### Backend Logs

```bash
cd backend
python -m uvicorn main:app --reload --port 8000 --log-level debug
```

#### Frontend Logs

- Open browser Developer Tools (F12)
- Check Console tab for errors
- Check Network tab for API calls

## 📊 Sample Data

The application includes comprehensive sample data:

- **Equipment Schedules**: 5 equipment items with various delay scenarios
- **Political Risks**: Sample news events for major countries
- **Risk Assessments**: Pre-calculated risk scores and recommendations

## 🔄 Development Mode

### Hot Reload

- Frontend: Changes auto-reload in browser
- Backend: Changes auto-restart server

### File Structure

```
ChainOps AI/
├── backend/           # FastAPI backend
│   ├── agents/        # AI agents
│   ├── database/      # MongoDB client
│   ├── models/        # Data schemas
│   └── main.py        # FastAPI app
├── frontend/          # React frontend
│   ├── src/
│   │   ├── components/    # React components
│   │   └── context/       # State management
└── README.md
```

## 🚀 Production Deployment

### Backend (FastAPI)

```bash
# Install production server
pip install gunicorn

# Run production server
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Frontend (React)

```bash
cd frontend
npm run build
# Serve build/ directory with nginx or similar
```

## 📞 Support

If you encounter issues:

1. Check this troubleshooting guide
2. Verify all prerequisites are installed
3. Check logs for specific error messages
4. Ensure ports 3000 and 8000 are available
5. Try running with sample data first (no API keys needed)

## 🎯 Next Steps

Once running successfully:

1. Explore the dashboard and world map
2. Try the chat assistant with sample queries
3. Generate and download reports
4. Check the thinking logs for AI reasoning
5. Customize with your own API keys for live data
