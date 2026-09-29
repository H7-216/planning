import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, render_template

app = Flask(__name__)

# URL source hébergeant le portage du jeu WebAssembly
TARGET_GAME_URL = "https://web.archive.org/web/20260901085540/https://quenq.com/apps/vice-city-online/"

@app.route('/')
def home():
    """Rendu de la page principale du portail universitaire"""
    return render_template('index.html')

@app.route('/game-proxy')
def game_proxy():
    """
    Scraper / Proxy Python utilisant BeautifulSoup 4 pour contourner 
    les restrictions X-Frame-Options et éviter l'écran noir dans l'iframe.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        # 1. Scraping HTML via Requests
        res = requests.get(TARGET_GAME_URL, headers=headers, timeout=10)
        
        # 2. Parsing et nettoyage HTML avec BeautifulSoup 4
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Injection de la balise <base> pour que les scripts .js et .wasm soient résolus correctement
        base_tag = soup.new_tag('base', href="https://web.archive.org/web/20260901085540/https://quenq.com/apps/vice-city-online/")
        if soup.head:
            soup.head.insert(0, base_tag)
        
        cleaned_html = str(soup)
        
        # 3. Création de la réponse Flask débloquée de toute restriction CORS / Frame
        response = Response(cleaned_html, content_type='text/html')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['X-Frame-Options'] = 'ALLOWALL'
        response.headers['Content-Security-Policy'] = "frame-ancestors '*'"
        return response

    except Exception as e:
        return Response(
            f"<html><body style='color:white;background:#000;text-align:center;padding:50px;'>"
            f"<h2>Erreur lors du chargement du proxy Python (BS4)</h2><p>{str(e)}</p>"
            f"</body></html>", 
            content_type='text/html'
        )

if __name__ == '__main__':
    print("🚀 Serveur Flask démarré sur http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
