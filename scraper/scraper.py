import requests
from bs4 import BeautifulSoup
import pandas as pd
import psycopg2  # For PostgreSQL integration

def scrape_tunisie_annonce(url):
    """
    Scrape a single page of listings.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    listings = soup.find_all('tr')  # Find all table rows (listings)

    data = []
    for listing in listings:
        cols = listing.find_all('td')  # Find all columns in the row
        if len(cols) == 13:  # Ensure this matches the structure of the table
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

def scrape_all_pages(base_url, num_pages):
    """
    Scrape multiple pages of listings.
    """
    all_data = []
    for page in range(1, num_pages + 1):
        url = f"{base_url}&rech_page_num={page}"  # Update the URL to include the page number
        print(f"Scraping page {page}...")
        page_data = scrape_tunisie_annonce(url)
        all_data.extend(page_data)
    return all_data

def save_to_postgres(data):
    """
    Save scraped data to PostgreSQL.
    """
    # Database connection details
    conn = psycopg2.connect(
        dbname="tunisie_annonce",  # Your database name
        user="postgres",      # Your PostgreSQL username
        password="1",  # Your PostgreSQL password
        host="localhost",          # Your database host
        port="5432"                # Your database port
    )
    cursor = conn.cursor()

    # Insert data into the table
    for item in data:
        cursor.execute("""
            INSERT INTO annonces (title, price, property_type, location, publication_date, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            item['title'],
            item['price'],
            item['property_type'],
            item['location'],
            item['publication_date'],
            item['link']
        ))

    # Commit and close the connection
    conn.commit()
    cursor.close()
    conn.close()
    print("Data saved to PostgreSQL database.")

# Base URL (same as your friend's)
base_url = "http://www.tunisie-annonce.com/AnnoncesImmobilier.asp?rech_cod_cat=1&rech_cod_rub=&rech_cod_typ=&rech_cod_sou_typ=&rech_cod_pay=TN&rech_cod_reg=&rech_cod_vil=&rech_cod_loc=&rech_prix_min=&rech_prix_max=&rech_surf_min=&rech_surf_max=&rech_age=&rech_photo=&rech_typ_cli=&rech_order_by=31"
num_pages = 100  # Number of pages to scrape

# Scrape all pages
listings_data = scrape_all_pages(base_url, num_pages)

# Save the data to PostgreSQL
save_to_postgres(listings_data)

# Optional: Save the data to a CSV file
df = pd.DataFrame(listings_data)
df.to_csv('tunisie_annonce_listings.csv', index=False)
print("Data saved to tunisie_annonce_listings.csv")