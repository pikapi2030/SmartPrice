# Project Architecture & Data Flow

This document details the architecture design and data flow of the real-time Price Comparison Web Application.

---

## 1. System Components & Layers

The diagram below maps the components of the platform. It uses light, high-contrast backgrounds with dark borders and text to ensure absolute readability in all viewer themes (dark or light mode).

```mermaid
graph TD
    %% High-Contrast Theme Styling
    classDef frontend fill:#EBF8FF,stroke:#3182CE,stroke-width:2px,color:#2B6CB0;
    classDef backend fill:#FAF5FF,stroke:#805AD5,stroke-width:2px,color:#553C9A;
    classDef db fill:#E6FFFA,stroke:#319795,stroke-width:2px,color:#234E52;
    classDef external fill:#FFF5F5,stroke:#E53E3E,stroke-width:2px,color:#9B2C2C;
    
    %% Frontend Components
    subgraph Frontend ["Frontend (Vite + React + Tailwind CSS)"]
        UI["Dashboard Page (App.jsx)"]
        Components["UI Components (Cards, Navbar, Filters)"]
        APIClient["API Client (Axios Service)"]
    end
    
    %% Backend Components
    subgraph Backend ["Backend API (FastAPI)"]
        Endpoints["API Endpoints (/api/search, /api/cache/clear)"]
        CacheMgr["Cache Handler (SQLAlchemy)"]
        ScrapeCtrl["Concurrent Scrape Controller"]
        
        subgraph Scrapers ["Scraping Engines"]
            AmScraper["Amazon Scraper (Selenium + BS4)"]
            FkScraper["Flipkart Scraper (Selenium + BS4)"]
            AccFilter["Accessory Filter (is_accessory_item)"]
            MockFallback["Mock Fallback Engine"]
        end
        
        subgraph Services ["Analytics & Match Services"]
            Matcher["Fuzzy Matcher (matcher.py)"]
            SpecExtractor["Spec Extractor (RAM & Storage)"]
            ModelValidator["Model Generation Validator"]
            Comparator["Comparator & Stats (comparator.py)"]
        end
    end
    
    %% Storage Components
    subgraph Storage ["Database Layer"]
        SQLite["SQLite Cache (comparison.db)"]
    end
    
    %% External Services
    subgraph External ["Websites Scraped"]
        AmazonIndia["Amazon India Web"]
        Flipkart["Flipkart Web"]
    end

    %% Component Interconnections
    UI --> Components
    UI --> APIClient
    APIClient <--> |HTTP / JSON| Endpoints
    
    Endpoints <--> CacheMgr
    CacheMgr <--> |SQL Queries| SQLite
    
    Endpoints --> ScrapeCtrl
    ScrapeCtrl --> |Runs in Thread 1| AmScraper
    ScrapeCtrl --> |Runs in Thread 2| FkScraper
    
    AmScraper -.-> |Filters items| AccFilter
    FkScraper -.-> |Filters items| AccFilter
    
    AmScraper -.-> |On Block/Timeout| MockFallback
    FkScraper -.-> |On Block/Timeout| MockFallback
    
    AmScraper <--> |Automates Browser| AmazonIndia
    FkScraper <--> |Automates Browser| Flipkart
    
    ScrapeCtrl --> Matcher
    Matcher --> SpecExtractor
    Matcher --> ModelValidator
    Matcher --> Comparator
    
    Matcher --> Endpoints

    %% Class Assignments
    class UI,Components,APIClient frontend;
    class Endpoints,CacheMgr,ScrapeCtrl,AmScraper,FkScraper,AccFilter,MockFallback,Matcher,SpecExtractor,ModelValidator,Comparator backend;
    class SQLite db;
    class AmazonIndia,Flipkart external;
```

---

## 2. Real-Time Data Flow (Search Sequence)

The sequence diagram below displays what happens step-by-step when a user inputs a query (e.g., `"Samsung Galaxy S24 Ultra"`):

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as FastAPI Backend
    participant DB as SQLite Cache
    participant SC as Scrape Controller
    participant Amazon as Amazon Scraper
    participant Flipkart as Flipkart Scraper
    participant Matcher as Fuzzy Matcher / Validator

    User->>API: POST /api/search { query: "Samsung Galaxy S24 Ultra" }
    API->>DB: Check Cache (query)
    
    alt Cache Hit (Within 1 Hour)
        DB-->>API: Return Cached JSON
        API-->>User: Return Matched Results (Source: cache)
    else Cache Miss / Expired
        API->>SC: Run Concurrent Scrapes
        par Amazon Scrape Thread
            SC->>Amazon: scrape_amazon("Samsung Galaxy S24 Ultra")
            Amazon->>Amazon: Fetch Search Page via Selenium
            Amazon->>Amazon: Parse & Filter Out Accessories
            Amazon-->>SC: Return List of Products (max 15)
        and Flipkart Scrape Thread
            SC->>Flipkart: scrape_flipkart("Samsung Galaxy S24 Ultra")
            Flipkart->>Flipkart: Fetch Search Page via Selenium
            Flipkart->>Flipkart: Parse & Filter Out Accessories
            Flipkart-->>SC: Return List of Products (max 15)
        end
        SC->>DB: Save/Update Cached Results
        SC->>Matcher: match_products(Amazon list, Flipkart list)
        
        Matcher->>Matcher: Parse specs (RAM/Storage) for each item
        Matcher->>Matcher: Validate brand and generation (e.g. S24 vs S25)
        Matcher->>Matcher: Calculate RapidFuzz token ratios
        Matcher->>Matcher: Filter price outliers & calculate savings stats
        
        Matcher-->>API: Return Final Comparisons & Statistics
        API-->>User: Return Matched Results (Source: live)
    end
```
# Project Architecture & Data Flow

This document details the architecture design and data flow of the real-time Price Comparison Web Application.

---

## 1. System Components & Layers

The diagram below maps the components of the platform. It uses light, high-contrast backgrounds with dark borders and text to ensure absolute readability in all viewer themes (dark or light mode).

```mermaid
graph TD
    %% High-Contrast Theme Styling
    classDef frontend fill:#EBF8FF,stroke:#3182CE,stroke-width:2px,color:#2B6CB0;
    classDef backend fill:#FAF5FF,stroke:#805AD5,stroke-width:2px,color:#553C9A;
    classDef db fill:#E6FFFA,stroke:#319795,stroke-width:2px,color:#234E52;
    classDef external fill:#FFF5F5,stroke:#E53E3E,stroke-width:2px,color:#9B2C2C;
    
    %% Frontend Components
    subgraph Frontend ["Frontend (Vite + React + Tailwind CSS)"]
        UI["Dashboard Page (App.jsx)"]
        Components["UI Components (Cards, Navbar, Filters)"]
        APIClient["API Client (Axios Service)"]
    end
    
    %% Backend Components
    subgraph Backend ["Backend API (FastAPI)"]
        Endpoints["API Endpoints (/api/search, /api/cache/clear)"]
        CacheMgr["Cache Handler (SQLAlchemy)"]
        ScrapeCtrl["Concurrent Scrape Controller"]
        
        subgraph Scrapers ["Scraping Engines"]
            AmScraper["Amazon Scraper (Selenium + BS4)"]
            FkScraper["Flipkart Scraper (Selenium + BS4)"]
            AccFilter["Accessory Filter (is_accessory_item)"]
            MockFallback["Mock Fallback Engine"]
        end
        
        subgraph Services ["Analytics & Match Services"]
            Matcher["Fuzzy Matcher (matcher.py)"]
            SpecExtractor["Spec Extractor (RAM & Storage)"]
            ModelValidator["Model Generation Validator"]
            Comparator["Comparator & Stats (comparator.py)"]
        end
    end
    
    %% Storage Components
    subgraph Storage ["Database Layer"]
        SQLite["SQLite Cache (comparison.db)"]
    end
    
    %% External Services
    subgraph External ["Websites Scraped"]
        AmazonIndia["Amazon India Web"]
        Flipkart["Flipkart Web"]
    end

    %% Component Interconnections
    UI --> Components
    UI --> APIClient
    APIClient <--> |HTTP / JSON| Endpoints
    
    Endpoints <--> CacheMgr
    CacheMgr <--> |SQL Queries| SQLite
    
    Endpoints --> ScrapeCtrl
    ScrapeCtrl --> |Runs in Thread 1| AmScraper
    ScrapeCtrl --> |Runs in Thread 2| FkScraper
    
    AmScraper -.-> |Filters items| AccFilter
    FkScraper -.-> |Filters items| AccFilter
    
    AmScraper -.-> |On Block/Timeout| MockFallback
    FkScraper -.-> |On Block/Timeout| MockFallback
    
    AmScraper <--> |Automates Browser| AmazonIndia
    FkScraper <--> |Automates Browser| Flipkart
    
    ScrapeCtrl --> Matcher
    Matcher --> SpecExtractor
    Matcher --> ModelValidator
    Matcher --> Comparator
    
    Matcher --> Endpoints

    %% Class Assignments
    class UI,Components,APIClient frontend;
    class Endpoints,CacheMgr,ScrapeCtrl,AmScraper,FkScraper,AccFilter,MockFallback,Matcher,SpecExtractor,ModelValidator,Comparator backend;
    class SQLite db;
    class AmazonIndia,Flipkart external;
```

---

## 2. Real-Time Data Flow (Search Sequence)

The sequence diagram below displays what happens step-by-step when a user inputs a query (e.g., `"Samsung Galaxy S24 Ultra"`):

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as FastAPI Backend
    participant DB as SQLite Cache
    participant SC as Scrape Controller
    participant Amazon as Amazon Scraper
    participant Flipkart as Flipkart Scraper
    participant Matcher as Fuzzy Matcher / Validator

    User->>API: POST /api/search { query: "Samsung Galaxy S24 Ultra" }
    API->>DB: Check Cache (query)
    
    alt Cache Hit (Within 1 Hour)
        DB-->>API: Return Cached JSON
        API-->>User: Return Matched Results (Source: cache)
    else Cache Miss / Expired
        API->>SC: Run Concurrent Scrapes
        par Amazon Scrape Thread
            SC->>Amazon: scrape_amazon("Samsung Galaxy S24 Ultra")
            Amazon->>Amazon: Fetch Search Page via Selenium
            Amazon->>Amazon: Parse & Filter Out Accessories
            Amazon-->>SC: Return List of Products (max 15)
        and Flipkart Scrape Thread
            SC->>Flipkart: scrape_flipkart("Samsung Galaxy S24 Ultra")
            Flipkart->>Flipkart: Fetch Search Page via Selenium
            Flipkart->>Flipkart: Parse & Filter Out Accessories
            Flipkart-->>SC: Return List of Products (max 15)
        end
        SC->>DB: Save/Update Cached Results
        SC->>Matcher: match_products(Amazon list, Flipkart list)
        
        Matcher->>Matcher: Parse specs (RAM/Storage) for each item
        Matcher->>Matcher: Validate brand and generation (e.g. S24 vs S25)
        Matcher->>Matcher: Calculate RapidFuzz token ratios
        Matcher->>Matcher: Filter price outliers & calculate savings stats
        
        Matcher-->>API: Return Final Comparisons & Statistics
        API-->>User: Return Matched Results (Source: live)
    end
```
