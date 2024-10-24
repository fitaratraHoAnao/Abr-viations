from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# URL du site à scraper
url = "https://www.btb.termiumplus.gc.ca/redac-chap?lang=fra&lettr=chapsect1&info0=1.4"

def scrape_abreviations():
    response = requests.get(url)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table", {"class": "widthFull"})
        
        abreviations = []
        for table in tables:
            rows = table.find_all("tr", {"class": "alignTop"})
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    abbr = cells[0].get_text(strip=True)
                    definition = cells[1].get_text(strip=True)
                    abreviations.append({"abreviation": abbr, "definition": definition})
        return abreviations
    else:
        return []

@app.route('/recherche', methods=['GET'])
def recherche():
    abreviation_param = request.args.get('abreviation')
    query_param = request.args.get('query')

    # Route pour récupérer toutes les abréviations
    if abreviation_param == 'liste':
        abreviations = scrape_abreviations()
        return jsonify(abreviations), 200

    # Route pour chercher une abréviation spécifique
    elif query_param:
        abreviations = scrape_abreviations()
        filtered_abreviation = next((abbr for abbr in abreviations if abbr['abreviation'].lower() == query_param.lower()), None)
        
        if filtered_abreviation:
            return jsonify(filtered_abreviation), 200
        else:
            return jsonify({"error": f"Aucune abréviation trouvée pour {query_param}"}), 404

    else:
        return jsonify({"error": "Paramètre 'abreviation' ou 'query' manquant"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
