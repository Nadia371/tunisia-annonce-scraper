# Tunisie Annonce Scraper

This project scrapes real estate listings from Tunisie Annonce and stores the data in a PostgreSQL database. The data is exposed via a Flask API and visualized in a Dash dashboard.

## Features
- Web scraping using BeautifulSoup and requests
- PostgreSQL database storage
- Flask API endpoints
- Interactive Dash dashboard

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Nadia371/tunisie-annonce-scraper.git
   cd tunisie-annonce-scraper
## Install dependencies:
pip install -r requirements.txt
## Usage
1. Run the scraper:
python scraper/scraper.py
2. Start the API:
python api/app.py
3. Launch the dashboard:
python dashboard/app.py
## API Endpoints
GET /annonces - Get all listings
POST /scrape - Trigger new scrape

## Dashboard
Access at http://localhost:8050 after starting. Features:

Price distribution charts

Property type analysis

Location filters

Real-time data refresh

## Database
PostgreSQL database with annonces table. Use PgAdmin to view data.
