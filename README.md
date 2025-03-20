# Tunisie Annonce Scraper

This project scrapes real estate listings from Tunisie Annonce and stores the data in a PostgreSQL database. The data is exposed via a Flask API.

## Features
- Scrapes listings using BeautifulSoup and requests.
- Saves data to a PostgreSQL database.
- Exposes data via a Flask API.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/tunisie-annonce-scraper.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Run the scraper:
   ```bash
   python scraper/scraper.py
   ```
2. Start the API:
   ```bash
   python api/app.py
   ```

## API Endpoints
- `GET /annonces`: Returns all listings.
- `POST /scrape`: Triggers a new scraping session.

## Database
- Data is stored in a PostgreSQL database. Use PgAdmin to view the `annonces` table.