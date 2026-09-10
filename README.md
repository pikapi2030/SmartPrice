# SmartPrice India - Price Comparison Platform

SmartPrice India is a real-time full-stack Price Comparison Web Application that allows users to search for products and compare prices from **Amazon India** and **Flipkart** simultaneously. It uses Selenium and BeautifulSoup for scraping, RapidFuzz for fuzzy string product matching, and SQLite for search caching.

---

## Features

- **Real-Time Scraping**: Queries Amazon India and Flipkart concurrently when a search is initiated.
- **Fuzzy Product Matching**: Matches similar titles across platforms using RapidFuzz (`Token Set Ratio`), avoiding false matches by verifying brands and specification differences (such as matching `128GB` and `256GB`).
- **Database Caching**: Caches scraping results in a SQLite database for 1 hour to prevent redundant requests and speed up repeated searches.
- **Interactive UI**: Sleek, modern dark-themed React application styled with glassmorphism components and Tailwind CSS.
- **Dynamic Statistics Panel**: Displays real-time matching rates, price difference highlights, cheapest store badges, and percentage savings.
- **Robust Fallback Engine**: Employs an intelligent mock data generator if scraping triggers anti-bot mechanisms (CAPTCHAs/blocks), ensuring the platform remains fully functional for demonstration.
- **Docker Support**: Containerized architecture for easy deployment.

---

## Directory Structure

```
comparisonPlatform/
├── backend/
│   ├── main.py                     # FastAPI server & routes
│   ├── config.py                   # System configurations
│   ├── requirements.txt            # Python dependencies
│   ├── Dockerfile                  # Python + Google Chrome container
│   ├── scrapers/
│   │   ├── amazon.py               # Amazon India scraper (Selenium)
│   │   ├── flipkart.py             # Flipkart scraper (Selenium)
│   │   └── mock_data.py            # Backup mock data generator
│   ├── services/
│   │   ├── matcher.py              # RapidFuzz comparison logic
│   │   └── comparator.py           # Statistical differences & sorting
│   └── database/
│       ├── connection.py           # SQLAlchemy database setup
│       └── models.py               # Cache & History schema
├── frontend/
│   ├── src/
│   │   ├── components/             # Reusable UI components
│   │   ├── services/
│   │   │   └── api.js              # Axios backend connection
│   │   ├── App.jsx                 # Core UI entrypoint
│   │   ├── main.jsx
│   │   └── index.css               # Tailwind & premium CSS overrides
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── Dockerfile                  # Nginx static server image
├── docker-compose.yml              # Container orchestration configuration
└── README.md                       # Documentation
```

---

## Quick Start (Docker Compose)

The easiest way to run the entire stack is using Docker Compose. Ensure you have Docker and Docker Compose installed.

1. **Clone the repository** and navigate to the project directory:
   ```bash
   cd comparisonPlatform
   ```

2. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```

3. **Access the application**:
   - Frontend Dashboard: [http://localhost:5173](http://localhost:5173)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs) (Interactive Swagger UI)

---

## Manual Setup (Local Development)

If you prefer to run the applications natively:

### 1. Prerequisites
- **Python 3.10+**
- **Node.js 20+** & **npm**
- **Google Chrome** browser installed on your machine (Selenium will locate it automatically).

### 2. Backend Setup
1. Navigate to the `backend` folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```
   *The server will start at `http://127.0.0.1:8000`.*

### 3. Frontend Setup
1. Open a new terminal window and navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The web client will launch at `http://localhost:5173`.*

---

## API Documentation

### `POST /api/search`
Scrapes and compares product listings.

- **Request Body**:
  ```json
  {
    "query": "iPhone 16"
  }
  ```
- **Response Structure**:
  ```json
  {
    "results": [
      {
        "product_name": "Apple iPhone 16 (Black, 128 GB)",
        "amazon_price": 79900.0,
        "flipkart_price": 79499.0,
        "best_platform": "Flipkart",
        "difference": 401.0,
        "percentage_difference": 0.5,
        "amazon_product": {
          "title": "Apple iPhone 16 (Black, 128 GB)",
          "price": 79900.0,
          "rating": 4.6,
          "url": "https://www.amazon.in/.../dp/B0...",
          "image": "https://images-eu.ssl-images-amazon.com/...",
          "platform": "Amazon"
        },
        "flipkart_product": {
          "title": "APPLE iPhone 16 (Black, 128 GB)",
          "price": 79499.0,
          "rating": 4.7,
          "url": "https://www.flipkart.com/...",
          "image": "https://rukminim2.flixcart.com/...",
          "platform": "Flipkart"
        },
        "similarity_score": 98.0
      }
    ],
    "stats": {
      "total_items": 15,
      "matched_items": 12,
      "amazon_cheaper_count": 4,
      "flipkart_cheaper_count": 8,
      "equal_count": 0,
      "avg_difference_percentage": 1.2
    },
    "source": "live"
  }
  ```

### `GET /api/history`
Returns a list of the 10 most recent unique search terms.

- **Response Structure**:
  ```json
  [
    {
      "query": "iphone 16",
      "timestamp": "2026-06-13 14:52:10"
    }
  ]
  ```

---

## Configuration Variables
Create a `.env` file in the `backend/` directory to customize configurations:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | String | `sqlite:///./comparison.db` | Connection string for SQLite DB |
| `SELENIUM_HEADLESS` | Boolean | `True` | Runs Chrome browser headlessly |
| `SELENIUM_TIMEOUT` | Integer | `15` | Max load time before scraper skips |
| `MOCK_FALLBACK` | Boolean | `True` | Emits mock details if blocked by stores |
| `MATCHING_THRESHOLD` | Float | `60.0` | Min string match confidence (0-100) |
| `CACHE_EXPIRY_SECONDS` | Integer | `3600` | Expiry duration (in sec) for query cache |
