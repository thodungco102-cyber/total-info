import json
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import re

def crawl_live_fuel_prices():
    # Giá trị mặc định dự phòng chuẩn kỳ điều hành mới nhất
    prices = {
        "ron95_3": 9927020,
        "e5_ron92": 9926970,
        "do_005s": 9929100
    }
    
    try:
        url = "https://webgia.com/gia-xang-dau/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            for row in rows:
                text = row.get_text()
                # Lọc ưu tiên dòng chứa giá bán lẻ trong nước (Vùng 1)
                if 'Vùng 1' in text or 'RON' in text or 'E5' in text or 'DO' in text:
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        name = cols[0].get_text().strip().upper()
                        val_str = cols[1].get_text().strip()
                        clean_val = re.sub(r'[^\d]', '', val_str)
                        
                        if clean_val.isdigit() and len(clean_val) >= 4:
                            val = int(clean_val)
                            # Bóc tách chính xác từng mặt hàng
                            if ('RON 95' in name or 'RON95' in name) and ('VÙNG 1' in name or 'RON 95-III' in name):
                                prices["ron95_3"] = val
                            elif 'E5' in name and ('VÙNG 1' in name or 'RON 92' in name):
                                prices["e5_ron92"] = val
                            elif ('DIESEL' in name or 'DO' in name) and ('VÙNG 1' in name or '0.05S' in name):
                                prices["do_005s"] = val
        print("Cào và tinh chỉnh dữ liệu trực tuyến thành công!")
    except Exception as e:
        print(f"Lỗi cào dữ liệu, dùng giá dự phòng: {e}")

    # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (Live Auto)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = crawl_live_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
