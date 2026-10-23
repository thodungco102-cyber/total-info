import json
import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

def get_fuel_prices_from_baomoi():
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
        "source": "BaoMoi Fuel Widget Live"
    }

    url = "https://baomoi.com/tien-ich-gia-xang-dau.epi"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }

    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                cols = row.find_all(['th', 'td'])
                row_text = " ".join([col.get_text(strip=True) for col in cols]).upper()
                
                if any(k in row_text for k in ["RON", "E5", "DIESEL", "DO"]):
                    numbers = re.findall(r'([\d]{2}[\.,][\d]{3})', row_text)
                    if numbers:
                        # Số đầu tiên trong bảng của Báo Mới chính là Giá Vùng 1 (chuẩn TP.HCM)
                        price = int(numbers[0].replace('.', '').replace(',', ''))
                        
                        if 15000 <= price <= 40000:
                            if ("95" in row_text or "E10" in row_text) and fuel_data["prices"]["ron95_3"] == 666888:
                                fuel_data["prices"]["ron95_3"] = price
                            elif ("E5" in row_text or "92" in row_text) and fuel_data["prices"]["e5_ron92"] == 666888:
                                fuel_data["prices"]["e5_ron92"] = price
                            elif ("DIESEL" in row_text or "DO 0,05S" in row_text) and fuel_data["prices"]["do_005s"] == 666888:
                                fuel_data["prices"]["do_005s"] = price

            print(f"=> [Thành công] Đã lấy dữ liệu chuẩn Vùng 1 từ Báo Mới!")
    except Exception as e:
        print(f"=> [Lỗi] Không thể cào dữ liệu: {e}")

    # Ghi file JSON
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n===> KẾT QUẢ GHI FILE JSON:\n{json.dumps(fuel_data, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    get_fuel_prices_from_baomoi()
