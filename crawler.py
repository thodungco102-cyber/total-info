import json
import re
from datetime import datetime
import pytz
import requests

def get_fuel_prices():
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
    # ❌ TẤT CẢ GIÁ MẶC ĐỊNH LÀ 666888 -> CHỈ ĐỔI KHI LẤY ĐƯỢC DATA TRỰC TUYẾN
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

    # Giả lập Browser User-Agent xịn để tránh bị firewall chặn IP
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    # Nguồn 1: Cào trực tiếp từ WebGia Petrolimex
    try:
        url = 'https://webgia.com/gia-xang-dau/petrolimex/'
        res = requests.get(url, headers=headers, timeout=12)
        
        if res.status_code == 200:
            html_text = res.text
            
            # Searcher RegEx lọc các chỉ số giá bán lẻ Vùng 1
            ron95_match = re.search(r'RON\s*95-III.*?>\s*([\d\.,]+)\s*<', html_text, re.IGNORECASE | re.DOTALL)
            e5_match = re.search(r'E5\s*RON\s*92-II.*?>\s*([\d\.,]+)\s*<', html_text, re.IGNORECASE | re.DOTALL)
            do_match = re.search(r'DO\s*0[,.]05S-II.*?>\s*([\d\.,]+)\s*<', html_text, re.IGNORECASE | re.DOTALL)
            fo_match = re.search(r'FO\s*3[,.]5S.*?>\s*([\d\.,]+)\s*<', html_text, re.IGNORECASE | re.DOTALL)

            fetched_any = False
            
            if ron95_match:
                val = int(re.sub(r'[^\d]', '', ron95_match.group(1)))
                if 10000 < val < 50000:
                    fuel_data["prices"]["ron95_3"] = val
                    fetched_any = True
                    
            if e5_match:
                val = int(re.sub(r'[^\d]', '', e5_match.group(1)))
                if 10000 < val < 50000:
                    fuel_data["prices"]["e5_ron92"] = val
                    fetched_any = True

            if do_match:
                val = int(re.sub(r'[^\d]', '', do_match.group(1)))
                if 10000 < val < 50000:
                    fuel_data["prices"]["do_005s"] = val
                    fetched_any = True

            if fo_match:
                val = int(re.sub(r'[^\d]', '', fo_match.group(1)))
                if 10000 < val < 50000:
                    fuel_data["prices"]["fo_35s"] = val
                    fetched_any = True

            if fetched_any:
                fuel_data["source"] = "WebGia - Petrolimex Live"
                print("=> [SUCCESS] Đã bóc tách thành công giá trực tuyến từ WebGia!")

    except Exception as e:
        print(f"=> [ERROR] Lỗi cào WebGia: {e}")

    # Ghi dữ liệu ra file fuel_data.json
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
        
    print(f"=> Kết quả ghi file: {json.dumps(fuel_data, ensure_ascii=False)}")

if __name__ == "__main__":
    get_fuel_prices()
