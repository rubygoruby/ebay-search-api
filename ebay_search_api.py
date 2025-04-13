from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def crawl_ebay(search_query, max_items):
    base_url = "https://www.ebay.com/sch/i.html"
    items = []
    page = 1
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.ebay.com/"
}
    
    while len(items) < max_items:
        params = {
            "_nkw": search_query,
            "_pgn": page,
            "_ipg": 100
        }

        # 재시도 로직 추가
        for attempt in range(3):  # 최대 3번 시도
            try:
                response = requests.get(base_url, params=params, headers=headers, timeout=30)
                if response.status_code != 200:
                    return {"error": f"페이지 {page} 요청 실패: {response.status_code}"}
                break  # 성공하면 루프 탈출
            except requests.RequestException as e:
                if attempt == 2:  # 마지막 시도에서도 실패하면 에러 반환
                    return {"error": f"네트워크 오류: {e}"}
                continue  # 실패하면 재시도
                
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
    
    return {"urls": items}        
    
        try:
            response = requests.get(base_url, params=params, headers=headers, timeout=30)
            if response.status_code != 200:
                return {"error": f"페이지 {page} 요청 실패: {response.status_code}"}
                
            soup = BeautifulSoup(response.text, 'html.parser')
            listings = soup.find_all('div', class_='s-item__wrapper')
            
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
