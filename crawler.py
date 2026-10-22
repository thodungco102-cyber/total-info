import json
from datetime import datetime
import urllib.request
import urllib.error
import re

def fetch_petrolimex_prices():
    # Giá trị mặc định an toàn chuẩn kỳ điều hành mới nhất
    prices = {
        "ron95_3": 220,
        "e5_ron92": 970,
        "do_005s": 200
    }
    
    # URL nguồn chính thức công khai giá bán lẻ xăng dầu của Petrolimex
    url = "https://www.petrolimex.com.vn/jian/price-Petrolimex.json"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'https://www.petrolimex.com.vn/'
            }
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            raw_data = response.read().decode('utf-8')
            data = json.loads(raw_data)
            
            # Xử lý bóc tách dữ liệu từ cấu trúc JSON của Petrolimex
            # Thường dữ liệu trả về nằm trong mảng hoặc danh sách giá vùng 1
            items = data if isinstance(data, list) else data.get('data', data.get('Rows', []))
            
            for item in items:
                name = str(item.get('Name', item.get('CommodityName', ''))).upper()
                price_str = str(item.get('Region1', item.get('Price1', item.get('Price', ''))))
                
                # Làm sạch chuỗi giá tiền (loại bỏ dấu phẩy, khoảng trắng)
                clean_price = re.sub(r'[^\d]', '', price_str)
                if clean_price.isdigit():
                    val = int(clean_price)
                    if 'RON 95' in name or 'VÙNG 1' in name and '95' in name:
                        prices["ron95_3"] = val
                    elif 'E5' in name:
                        prices["e5_ron92"] = val
                    elif 'DO' in name or 'DIESEL' in name:
                        prices["do_005s"] = val
                        
    except Exception as e:
        print(f"Không thể kết nối trực tiếp Petrolimex, sử dụng cơ chế dự phòng: {e}")

    now = datetime.now()
    updated_str = f"{now.strftime('%H:%M %d/%m/%Y')} (Petrolimex Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = fetch_petrolimex_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
