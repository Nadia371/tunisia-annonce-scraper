from flask import Flask, jsonify
import pandas as pd

app = Flask(__name__)

# Load scraped data
df = pd.read_csv('tunisie_annonce_listings.csv')

@app.route('/annonces', methods=['GET'])
def get_annonces():
    """
    Endpoint to return all listings.
    """
    return jsonify(df.to_dict(orient='records'))

@app.route('/scrape', methods=['POST'])
def scrape():
    """
    Endpoint to trigger a new scraping session.
    """
    # Call your scraping function here
    # For example:
    # scrape_all_pages(base_url, num_pages)
    return jsonify({"message": "Scraping completed"})

if __name__ == '__main__':
    app.run(debug=True)