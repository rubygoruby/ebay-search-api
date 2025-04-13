from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def crawl_ebay(search_query, max_items):
    base_url = "https://www.ebay.com/sch/i.html"
    items = []
    page = 1
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
    }
    
    while len(items) < max_items:
        params = {
            "_nkw": search_query,
            "_pgn": page,
            "_ipg": 100
        }
        
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            if response.status_code != 200:
                return {"error": f"페이지 {page} 요청 실패: {response.status_code}"}
                
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('div', class_='s-item__info')
            
            if not listings:
                break
                
            for listing in listings:
                if len(items) >= max_items:
                    break
                    
                try:
                    url_elem = listing.find('a', class_='s-item__link')
                    url = url_elem['href'] if url_elem else "N/A"
                    
                    if url != "N/A":
                        items.append(url)
                except Exception as e:
                    continue
            
            page += 1
            
        except requests.RequestException as e:
            return {"error": f"네트워크 오류: {e}"}
    
    return {"urls": items}

@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query')
    max_items = int(request.args.get('max_items', 10))
    
    if not search_query:
        return jsonify({"error": "검색어가 필요합니다."}), 400
    
    result = crawl_ebay(search_query, max_items)
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
