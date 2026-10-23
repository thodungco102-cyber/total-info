import json
import re
from datetime import datetime
import pytz
import requests

def get_fuel_prices():
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        news_url = "https://vietnamnet.vn/kinh-doanh/thi-truong"
        res = requests.get(news_url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            html = res.text
            
            # Tìm tất cả các chuỗi số có dạng giá tiền (ví dụ: 21.350 hoặc 21350) nằm gần từ khóa
            # Lọc khắt khe: Giá xăng dầu phải nằm trong khoảng từ 15,000 đến 35,000 VNĐ
            
            def parse_valid_price(text_snippet):
                numbers = re.findall(r'([\d\.]{5,7})', text_snippet)
                for num_str in numbers:
                    clean_val = int(num_str.replace('.', '').replace(',', ''))
                    if 15000 <= clean_val <= 35000: # Khoảng giá chuẩn của xăng dầu VN
                        return clean_val
                return 666888

            # Cắt các đoạn văn bản chứa từ khóa xăng dầu để quét chính xác hơn
            for line in html.split('\n'):
                line_upper = line.upper()
                if "RON 95" in line_upper or "RON95" in line_upper:
                    val = parse_valid_price(line)
                    if val != 666888: fuel_data["prices"]["ron95_3"] = val
                elif "E5" in line_upper or "RON 92" in line_upper:
                    val = parse_valid_price(line)
                    if val != 666888: fuel_data["prices"]["e5_ron92"] = val
                elif "DIESEL" in line_upper or "DO 0" in line_upper:
                    val = parse_valid_price(line)
                    if val != 666888: fuel_data["prices"]["do_005s"] = val

            if fuel_data["prices"]["ron95_3"] != 666888 or fuel_data["prices"]["e5_ron92"] != 666888:
                fuel_data["source"] = "VietNamNet Filtered Live"
                print("=> [Thành công] Lọc và bóc tách thành công giá xăng dầu chuẩn!")

    except Exception as e:
        print(f"Lỗi khi cào dữ liệu: {e}")

    # Ghi kết quả ra file JSON
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n===> KẾT QUẢ CUỐI CÙNG:\n{json.dumps(fuel_data, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    get_fuel_prices()
