import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

URL = "https://www.petrolimex.com.vn/"

def extract_number(text):
    text = text.replace(".", "").replace(",", "")
    m = re.search(r"\d{4,6}", text)
    return int(m.group()) if m else None

def crawl_petrolimex():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.petrolimex.com.vn/"
    }
    
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()
    
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    
    prices = {
        "ron95_3": None,
        "e5_ron92": None,
        "do_005s": None
    }
    
    # Biểu thức chính quy quét dữ liệu giá trên trang
    patterns = {
        "ron95_3": r"RON\s*95[^\d]*(\d{2}[.,]\d{3})",
        "e5_ron92": r"E5[^\d]*RON\s*92[^\d]*(\d{2}[.,]\d{3})",
        "do_005s": r"DO\s*0[.,]05S[^\d]*(\d{2}[.,]\d{3})",
    }
    
    for key, pattern in patterns.items():
        m = re.search(pattern, text, flags=re.I)
        if m:
            prices[key] = extract_number(m.group(1))
            
    return prices

def save_data(prices):
    vn_tz = timezone(timedelta(hours=7))
    data = {
        "updated_at": datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y (Live Crawl)"),
        "source": "Petrolimex",
        "prices": prices
    }
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật thành công file fuel_data.json")

if __name__ == "__main__":
    try:
        prices = crawl_petrolimex()
        # Nếu thiếu dữ liệu do thay đổi cấu trúc web, ném lỗi để giữ nguyên trạng thái an toàn
        if not all(prices.values()):
            raise Exception("Không bóc tách được đầy đủ các chỉ số giá xăng dầu!")
        save_data(prices)
    except Exception as e:
        print("Lỗi Crawler:", e)
        raise e
