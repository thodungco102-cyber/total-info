import json
import re
from datetime import datetime
import pytz
import requests

def fetch_online_fuel_prices():
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
    # Mặc định ban đầu dùng mã 666888
    fuel_data = {
        "updated_at": now_vn.strftime("%H:%M %d/%m/%Y"),
        "prices": {
            "ron95_3": 666888,
            "e5_ron92": 666888,
            "do_005s": 666888,
            "fo_35s": 666888
        },
        "source": "Fetch Error (666888)"
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    # =========================================================================
    # CHUYẾN 1: BÓC TÁCH TỪ KẾT QUẢ TÌM KIẾM DỮ LIỆU MỞ (MÔ PHỎNG GOOGLE SEARCH)
    # =========================================================================
    try:
        search_url = "https://html.duckduckgo.com/html/?q=gia+xang+dau+petrolimex+hom+nay"
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code == 200:
            text = res.text
            ron95 = re.search(r'RON\s*95[-–\s]*III[^\d]*([\d\.,]{5,7})', text, re.I)
            e5 = re.search(r'E5\s*RON\s*92[^\d]*([\d\.,]{5,7})', text, re.I)
            do = re.search(r'Diesel[^\d]*([\d\.,]{5,7})', text, re.I)
            
            if ron95:
                v = int(re.sub(r'[^\d]', '', ron95.group(1)))
                if 15000 <= v <= 35000: fuel_data["prices"]["ron95_3"] = v
            if e5:
                v = int(re.sub(r'[^\d]', '', e5.group(1)))
                if 15000 <= v <= 35000: fuel_data["prices"]["e5_ron92"] = v
            if do:
                v = int(re.sub(r'[^\d]', '', do.group(1)))
                if 15000 <= v <= 35000: fuel_data["prices"]["do_005s"] = v
                
            if fuel_data["prices"]["ron95_3"] != 666888:
                fuel_data["source"] = "Search Engine Live Data"
                print("=> [Thành công] Lấy dữ liệu qua Search Engine!")
    except Exception as e:
        print(f"Lỗi nguồn Search: {e}")

    # =========================================================================
    # CHUYẾN 2: NẾU SEARCH VẪN CHƯA THẤY, QUÉT NGUỒN CỔNG API MỞ THỊ TRƯỜNG
    # =========================================================================
    if fuel_data["prices"]["ron95_3"] == 666888:
        try:
            api_url = "https://api.pvoi.vn/api/price/current" # Cổng Dầu khí PVOIL Live
            res = requests.get(api_url, headers=headers, timeout=8)
            if res.status_code == 200:
                json_data = res.json()
                if "data" in json_data:
                    for item in json_data["data"]:
                        name = str(item.get("name", "")).upper()
                        price = int(item.get("price", 0))
                        if "RON 95" in name and price > 10000: fuel_data["prices"]["ron95_3"] = price
                        elif "E5" in name and price > 10000: fuel_data["prices"]["e5_ron92"] = price
                        elif "DIESEL" in name or "DO" in name: fuel_data["prices"]["do_005s"] = price
                    fuel_data["source"] = "PVOIL Official API"
                    print("=> [Thành công] Lấy dữ liệu qua PVOIL API!")
        except Exception as e:
            print(f"Lỗi nguồn API: {e}")

    # =========================================================================
    # CHUYẾN 3: TỰ ĐỘNG BÓC TÁCH TỪ TRANG TIN TỨC VNEPRESS THỊ TRƯỜNG
    # =========================================================================
    if fuel_data["prices"]["ron95_3"] == 666888:
        try:
            vne_url = "https://vnexpress.net/chu-de/gia-xang-dau-2444"
            res = requests.get(vne_url, headers=headers, timeout=8)
            if res.status_code == 200:
                # Bóc tách chỉ số từ bài báo điều hành giá xăng mới nhất
                m_ron = re.search(r'RON\s*95[^\d]*([\d\.]{5,6})', res.text, re.I)
                m_e5 = re.search(r'E5\s*RON\s*92[^\d]*([\d\.]{5,6})', res.text, re.I)
                m_do = re.search(r'dầu\s*diesel[^\d]*([\d\.]{5,6})', res.text, re.I)
                
                if m_ron: fuel_data["prices"]["ron95_3"] = int(m_ron.group(1).replace('.', ''))
                if m_e5: fuel_data["prices"]["e5_ron92"] = int(m_e5.group(1).replace('.', ''))
                if m_do: fuel_data["prices"]["do_005s"] = int(m_do.group(1).replace('.', ''))
                
                if fuel_data["prices"]["ron95_3"] != 666888:
                    fuel_data["source"] = "VnExpress Market Feed"
                    print("=> [Thành công] Lấy dữ liệu qua VnExpress Feed!")
        except Exception as e:
            print(f"Lỗi nguồn VnExpress: {e}")

    # Ghi kết quả cuối cùng ra file JSON
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n===> KẾT QUẢ BOT CÀO DỮ LIỆU:\n{json.dumps(fuel_data, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    fetch_online_fuel_prices()
