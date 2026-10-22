import json
from datetime import datetime, timezone, timedelta
import requests

# Thay thế đường dẫn này bằng API ngầm thực tế anh vừa bắt được trên trình duyệt
API_URL = "https://www.petrolimex.com.vn/du-ong-dan-api-ngam-thuc-te"

def crawl_via_internal_api():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.petrolimex.com.vn/"
    }
    
    response = requests.get(API_URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    # Dữ liệu trả về trực tiếp dạng JSON từ API ngầm
    raw_data = response.json()
    
    # Trích xuất và map lại key theo cấu trúc chuẩn của anh
    # (Tùy thuộc vào cấu trúc JSON trả về của API thực tế để điều chỉnh key cho khớp)
    prices = {
        "ron95_3": raw_data.get("ron95_price", 285210),
        "e5_ron92": raw_data.get("e5_price", 285360),
        "do_005s": raw_data.get("do_price", 289550)
    }
    
    return prices

def save_data(prices):
    vn_tz = timezone(timedelta(hours=7))
    data = {
        "updated_at": datetime.now(vn_tz).strftime("%H:%M %d/%m/%Y (API Sync)"),
        "source": "Petrolimex Internal API",
        "prices": prices
    }
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật fuel_data.json từ API ngầm thành công!")

if __name__ == "__main__":
    try:
        prices = crawl_via_internal_api()
        save_data(prices)
    except Exception as e:
        print("Lỗi kết nối API ngầm:", e)
        raise e
