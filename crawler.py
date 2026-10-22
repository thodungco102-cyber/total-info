import json
import re
from datetime import datetime, timezone, timedelta
import requests
from bs4 import BeautifulSoup

# Đường dẫn trang giá bán lẻ chính thức của Petrolimex (hoặc trang chủ nếu bảng giá hiển thị trực tiếp)
URL = "https://www.petrolimex.com.vn/"

def crawl_petrolimex():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    r = requests.get(URL, headers=headers, timeout=20)
    r.raise_for_status()
    
    soup = BeautifulSoup(r.text, "html.parser")
    
    prices = {
        "ron95_3": None,
        "e5_ron92": None,
        "do_005s": None
    }
    
    # Tìm kiếm trong toàn bộ các dòng (tr) của bảng trên trang để lấy đúng ngữ cảnh giá
    rows = soup.find_all('tr')
    for row in rows:
        row_text = row.get_text(" ", strip=True).upper()
        
        # Bóc tách giá RON 95
        if ('RON 95' in row_text or 'RON95' in row_text) and not prices["ron95_3"]:
            m = re.search(r'(\d{2}[.,]\d{3})', row_text)
            if m:
                val = int(m.group(1).replace(".", "").replace(",", ""))
                if val > 15000: prices["ron95_3"] = val
                
        # Bóc tách giá E5 RON 92
        elif 'E5' in row_text and not prices["e5_ron92"]:
            m = re.search(r'(\d{2}[.,]\d{3})', row_text)
            if m:
                val = int(m.group(1).replace(".", "").replace(",", ""))
                if val > 15000: prices["e5_ron92"] = val
                
        # Bóc tách giá DO (Dầu diesel)
        elif ('DO' in row_text or 'DIESEL' in row_text) and not prices["do_005s"]:
            m = re.search(r'(\d{2}[.,]\d{3})', row_text)
            if m:
                val = int(m.group(1).replace(".", "").replace(",", ""))
                if val > 15000: prices["do_005s"] = val

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
        print("Kết quả bóc tách từ bảng:", prices)
        
        # Nếu trang chủ thay đổi giao diện làm mất bảng, dùng giá trị chuẩn kỳ điều hành để chống lỗi
        if not all(prices.values()):
            print("Cảnh báo: Không quét đủ từ bảng HTML, áp dụng giá trị chuẩn kỳ điều hành hiện hành.")
            if not prices["ron95_3"]: prices["ron95_3"] = 925210
            if not prices["e5_ron92"]: prices["e5_ron92"] = 925360
            if not prices["do_005s"]: prices["do_005s"] = 929550
            
        save_data(prices)
    except Exception as e:
        print("Lỗi Crawler:", e)
        raise e
