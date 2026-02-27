<div align="center">
  <img src="frontend/public/logo.png" alt="ChainOps AI Logo" width="200"/>
</div>

# ChainOps AI - Multi-Agent Supply Chain Risk Intelligence Platform

ChainOps AI is a proof-of-concept Agentic AI application for real-time supply chain risk intelligence, built using only free agents and APIs. It helps expeditors monitor and assess supply chain risks across multiple domains in near real time.

## 🌍 Core Features

- **Real-time Risk Monitoring**: Track political, schedule, and logistics risks
- **Multi-Agent Architecture**: 4 specialized AI agents working together
- **Interactive Dashboard**: World map visualization with risk heatmaps
- **Natural Language Queries**: Chat with AI assistant for risk analysis
- **Comprehensive Reports**: Generate and download detailed risk assessments
- **Free APIs**: Uses only free-tier services (no credit card required)

## 🤖 Multi-Agent System

### 1. Assistant Agent

- Handles greetings, help, and general queries
- Uses OpenAI GPT for natural language processing
- Routes queries to appropriate specialized agents

### 2. Scheduler Agent

- Analyzes equipment schedule data
- Identifies delivery delays and risk levels (1-5)
- Returns structured JSON with schedule risks

### 3. Political Risk Agent

- Uses NewsData.io and GNews (free APIs) for news analysis
- Analyzes political/geopolitical events by country
- Assigns likelihood scores based on recentness and severity
- Provides citations and source links

### 4. Reporting Agent

- Combines outputs from other agents
- Generates comprehensive risk reports
- Creates downloadable PDF/DOCX reports
- Formats data for visualization

## 🛠 Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB (Community Edition or Atlas Free Tier)
- **Charts & Maps**: react-simple-maps, recharts
- **News APIs**: NewsData.io, GNews (free tiers)
- **LLM**: OpenAI free tier
- **Reporting**: python-docx, reportlab

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ and npm
- Python 3.8+
- MongoDB (local or Atlas free tier)

### Installation

1. **Clone and install dependencies:**

```bash
git clone <repository-url>
cd ChainOps-AI
npm run install-all
```

2. **Set up environment variables:**

```bash
cd backend
cp env.example .env
# Edit .env with your API keys (optional for demo)
```

3. **Start the application:**

```bash
npm run dev
```

This will start both the backend (port 8000) and frontend (port 3000).

### API Keys (Optional)

The application works with sample data by default. For live data, add these to `backend/.env`:

```env
# OpenAI API Key (for enhanced responses)
OPENAI_API_KEY=your-openai-key

# News API Keys (for live political risk data)
NEWSDATA_API_KEY=your-newsdata-key
GNEWS_API_KEY=your-gnews-key

# MongoDB (optional, uses file fallback)
MONGODB_URI=mongodb://localhost:27017/chainops_ai
```

## 📱 Usage

### Dashboard

- View global risk heatmap
- See real-time political and schedule risks
- Interact with chat assistant
- Monitor risk trends with charts

### Chat Assistant

Ask natural language questions like:

- "What are the political risks?"
- "Which equipment has delivery delays?"
- "Show me the risk summary"
- "Generate a comprehensive report"

### Reports

- View all generated reports
- Filter by type and search
- Download PDF reports
- Track report history

### Thinking Logs

- Monitor AI agent reasoning
- View conversation history
- Track decision-making process

## 🔧 Development

### Backend Development

```bash
cd backend
python -m uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
npm start
```

### Database Setup

The application uses MongoDB but falls back to file storage if unavailable. For production:

1. Install MongoDB locally or use MongoDB Atlas free tier
2. Update `MONGODB_URI` in `.env`
3. The app will automatically create necessary indexes

## 📊 Sample Data

The application includes sample data for demonstration:

- Equipment schedules with various delay scenarios
- Political risk events for major countries
- Risk assessments and recommendations

## 🎯 Key Features

### Risk Assessment

- **Political Risks**: Trade policies, sanctions, labor disputes
- **Schedule Risks**: Delivery delays, timeline impacts
- **Combined Analysis**: Integrated risk scoring

### Visualization

- **World Map**: Color-coded risk levels by country
- **Charts**: Risk distribution and trend analysis
- **Tables**: Detailed risk breakdowns with citations

### Reporting

- **PDF Generation**: Professional risk reports
- **Multiple Formats**: Political, schedule, and combined reports
- **Downloadable**: Easy sharing and archiving

## 🔒 Security & Privacy

- All API calls use HTTPS
- No sensitive data stored permanently
- Session-based data management
- Free-tier APIs only (no credit card required)

## 🤝 Contributing

This is a proof-of-concept project. Contributions welcome for:

- Additional risk data sources
- Enhanced visualization features
- New agent capabilities
- UI/UX improvements

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

For issues or questions:

1. Check the sample data is loading correctly
2. Verify API keys are properly configured
3. Ensure MongoDB is running (or using file fallback)
4. Check browser console for frontend errors
5. Check backend logs for API errors

## 🔮 Future Enhancements

- Real-time data streaming
- Advanced ML risk prediction
- Integration with more data sources
- Mobile-responsive design improvements
- Multi-language support
- Advanced reporting templates
