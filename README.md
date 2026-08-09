<p align="center">
  <img src="https://img.shields.io/badge/Status-Phase%202%20Complete-brightgreen?style=for-the-badge" alt="Status"/>
  <img src="https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Playwright-Latest-2EAD33?style=for-the-badge&logo=playwright" alt="Playwright"/>
</p>

# 🛒 SmartBuy AI — Autonomous AI Shopping Agent

**SmartBuy AI** is an autonomous AI-powered shopping agent that browses e-commerce websites (Amazon & Flipkart) in real time, extracts product data, and presents it through a sleek, modern dashboard — just like a human would shop, but automated.

> **Current Status:** Phase 1 (Architecture) ✅ and Phase 2 (Browser Automation) ✅ are complete. Phase 3 (AI Reasoning with LangGraph, RAG, and Database) is planned.

---

## ✨ Features

### Phase 1 — Project Architecture
- ⚡ **FastAPI Backend** with modular route/service/config architecture
- ⚛️ **React + Vite Frontend** with a premium dark-mode glassmorphism UI
- 🔌 **REST API** with CORS support for seamless frontend-backend communication
- 📁 **Clean separation** of concerns (routes → services → models)

### Phase 2 — Browser Automation
- 🌐 **Headless Chromium** browser controlled via Playwright (Python)
- 🔍 **Real-time product search** on Amazon India and Flipkart
- 🧠 **Layout-agnostic DOM extraction** — uses intelligent JavaScript evaluation instead of fragile CSS selectors
- 🖼️ **Product images, prices, ratings, and review counts** extracted accurately
- 📸 **Live screenshots** of the browser viewport from the dashboard
- 🛡️ **Anti-detection** with realistic User-Agent headers and human-like scrolling
- 🔄 **Singleton browser manager** — one persistent browser instance for all operations

---

## 🏗️ Architecture

```
shopping-agent/
├── backend/
│   ├── run.py                          # Uvicorn entry point
│   ├── requirements.txt                # Python dependencies
│   └── app/
│       ├── main.py                     # FastAPI app with lifespan management
│       ├── config/
│       │   └── settings.py             # Environment configuration
│       ├── models/
│       │   └── schemas.py              # Pydantic data models
│       ├── routes/
│       │   ├── agent.py                # AI agent routes (Phase 3)
│       │   └── browser.py              # Browser automation endpoints
│       ├── services/
│       │   ├── agent_service.py        # AI service placeholder (Phase 3)
│       │   └── browser/
│       │       ├── browser_manager.py  # Playwright singleton manager
│       │       ├── base_scraper.py     # Shared scraping utilities
│       │       ├── amazon.py           # Amazon India scraper
│       │       └── flipkart.py         # Flipkart scraper
│       └── utils/
│           └── helpers.py              # Utility functions
│
├── frontend/
│   ├── index.html                      # Entry HTML
│   ├── package.json                    # Node dependencies
│   ├── vite.config.js                  # Vite configuration
│   └── src/
│       ├── main.jsx                    # React entry point
│       ├── App.jsx                     # Root component with routing
│       ├── index.css                   # Global styles (dark theme)
│       ├── api/
│       │   └── client.js              # Axios API client
│       ├── components/
│       │   ├── Navbar.jsx             # Navigation bar
│       │   ├── BrowserPanel.jsx       # Browser automation dashboard
│       │   ├── ChatInput.jsx          # Chat interface (Phase 3)
│       │   └── ReasoningPanel.jsx     # AI reasoning display (Phase 3)
│       └── pages/
│           └── Home.jsx               # Main dashboard page
│
├── docs/                               # Documentation assets
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**

### 1. Clone the Repository

```bash
git clone https://github.com/Sankhyaan/SmartBuy-AI-Autonomous-AI-Shopping-Agent.git
cd SmartBuy-AI-Autonomous-AI-Shopping-Agent
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser
python -m playwright install chromium

# Start the server
python run.py
```

The API server will be running at `http://localhost:8000`.

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be running at `http://localhost:5173`.

---

## 🔌 API Endpoints

### Browser Automation

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/browser/start` | Launch headless Chromium browser |
| `POST` | `/browser/stop` | Close the browser instance |
| `GET` | `/browser/status` | Get browser running status & current URL |
| `POST` | `/browser/amazon/search` | Search products on Amazon India |
| `POST` | `/browser/flipkart/search` | Search products on Flipkart |
| `POST` | `/browser/amazon/extract` | Extract products from current Amazon page |
| `POST` | `/browser/flipkart/extract` | Extract products from current Flipkart page |
| `GET` | `/browser/screenshot` | Capture a screenshot of the browser viewport |

### Request/Response Example

**Search Request:**
```json
POST /browser/flipkart/search
{
  "query": "laptop",
  "max_results": 10
}
```

**Response:**
```json
{
  "query": "laptop",
  "source": "Flipkart",
  "total": 10,
  "products": [
    {
      "title": "ASUS Vivobook 15 Intel Core i3 13th Gen...",
      "price": "₹42,990",
      "rating": "4.3",
      "rating_count": "1,245",
      "url": "https://www.flipkart.com/...",
      "image_url": "https://rukminim2.flixcart.com/...",
      "source": "Flipkart"
    }
  ]
}
```

Both Amazon and Flipkart return the **same standardized `ProductItem` schema**, making it easy to compare products across stores.

---

## 🧠 How the Scraping Works

The scraper uses a **layout-agnostic extraction engine** that doesn't rely on Flipkart or Amazon's CSS class names (which change frequently). Instead, it:

1. **Navigates** to the search URL using Playwright's headless Chromium
2. **Scrolls** the page to trigger lazy-loaded images
3. **Evaluates JavaScript** inside the browser to:
   - Find all product links (`a[href*="/p/"]` for Flipkart, `div[data-component-type="s-search-result"]` for Amazon)
   - Traverse up the DOM tree to find the parent container holding the image + text
   - Use **text heuristics** to extract Title (longest text), Price (₹ symbol + regex), Rating (pattern like `4.5(1,234)`), and Images
4. **Returns structured JSON** using a standardized schema

This approach is **resilient to CSS class changes** — even when Flipkart obfuscates their class names, the scraper still works.

---

## 🎨 UI Preview

The frontend features a premium dark-mode dashboard with:
- **Store selector** (Amazon / Flipkart toggle)
- **Real-time search** with animated product cards
- **Product cards** showing image, title, price, rating, and a link to the original listing
- **Browser status indicator** with live URL bar
- **Screenshot modal** for viewing the headless browser viewport

---

## 🗺️ Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1** | ✅ Complete | Project architecture, FastAPI + React setup, UI design |
| **Phase 2** | ✅ Complete | Browser automation with Playwright, Amazon & Flipkart scrapers |
| **Phase 3** | 🔜 Planned | LangGraph AI reasoning, RAG pipeline, PostgreSQL, Authentication |

### Phase 3 will include:
- 🤖 **LangGraph** for multi-step AI reasoning and decision-making
- 📚 **RAG (Retrieval-Augmented Generation)** for product knowledge
- 🗄️ **PostgreSQL** database for persistent product & session storage
- 🔐 **User authentication** and session management
- 💬 **Natural language shopping** — "Find me a laptop under ₹50,000 with good reviews"

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Axios, CSS (Dark Glassmorphism) |
| **Backend** | Python 3.13, FastAPI, Uvicorn |
| **Browser Automation** | Playwright (Headless Chromium) |
| **Data Models** | Pydantic v2 |
| **Future** | LangGraph, LangChain, PostgreSQL, pgvector |

