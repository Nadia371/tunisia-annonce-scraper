import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2
from time import sleep

def scrape_tunisie_annonce(url):
    """
    Scrape a single page of listings.
    """
    try:
        response = requests.get(url, timeout=10)  # Add timeout to avoid hanging
        if response.status_code != 200:
            print(f"Failed to retrieve page. Status code: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('tr')  # Find all table rows (listings)

        data = []
        for listing in listings:
            cols = listing.find_all('td')
            if len(cols) == 13:  # Ensure this matches the table structure
                title = cols[7].find('a').text.strip() if cols[7].find('a') else "N/A"
                price = cols[9].text.strip() if cols[9].text else "N/A"
                property_type = cols[5].text.strip() if cols[5].text else "N/A"
                location = cols[1].find('a').text.strip() if cols[1].find('a') else "N/A"
                publication_date = cols[11].text.strip() if cols[11].text else "N/A"
                link = cols[7].find('a')['href'] if cols[7].find('a') else "N/A"

                data.append({
                    'title': title,
                    'price': price,
                    'property_type': property_type,
                    'location': location,
                    'publication_date': publication_date,
                    'link': link
                })

        return data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

def scrape_all_pages(base_url):
    """
    Scrape all pages dynamically until no more listings are found.
    """
    all_data = []
    page = 1
    while True:
        url = f"{base_url}&rech_page_num={page}"
        print(f"Scraping page {page}...")
        page_data = scrape_tunisie_annonce(url)
        
        # Stop if no data is returned (empty page)
        if not page_data:
            print(f"No more listings found on page {page}. Stopping.")
            break
        
        all_data.extend(page_data)
        page += 1
        sleep(1)  # Add a delay to avoid overwhelming the server

    return all_data

def save_to_postgres(data):
    """
    Save scraped data to PostgreSQL.
    """
    try:
        conn = psycopg2.connect(
            dbname="tunisie_annonce",
            user="postgres",
            password="1",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()

        # Create table if it doesn't exist (optional, run once)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS annonces (
                id SERIAL PRIMARY KEY,
                title TEXT,
                price TEXT,
                property_type TEXT,
                location TEXT,
                publication_date TEXT,
                link TEXT
            )
        """)

        # Insert data
        for item in data:
            cursor.execute("""
                INSERT INTO annonces (title, price, property_type, location, publication_date, link)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING  -- Avoid duplicates if rerunning
            """, (
                item['title'],
                item['price'],
                item['property_type'],
                item['location'],
                item['publication_date'],
                item['link']
            ))

        conn.commit()
        print("Data saved to PostgreSQL database.")
    except Exception as e:
        print(f"Error saving to PostgreSQL: {e}")
    finally:
        cursor.close()
        conn.close()

# Base URL
base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=TN&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31"

# Scrape all pages dynamically
listings_data = scrape_all_pages(base_url)

# Save to PostgreSQL
save_to_postgres(listings_data)

# Optional: Save to CSV
df = pd.DataFrame(listings_data)
df.to_csv('tunisie_annonce_listings.csv', index=False)
print("Data saved to tunisie_annonce_listings.csv")