import json
from datetime import datetime, timedelta, timezone
import cloudscraper
from bs4 import BeautifulSoup
import re

def crawl_official_fuel_prices():
    # Giá trị mặc định dự phòng an toàn
    prices = {
        "ron95_3": 9925210,
        "e5_ron92": 9925360,
        "do_005s": 9929550
    }
    
    # Khởi tạo cloudscraper để vượt qua tường lửa Cloudflare/WAF (chống lỗi 403)
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    try:
        url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
        response = scraper.get(url, timeout=15)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            rows = soup.find_all('tr')
            found_count = 0
            
            for row in rows:
                row_text = row.get_text()
                if any(k in row_text.upper() for k in ['RON 95', 'E5', 'DO', 'DIESEL']):
                    cols = row.find_all(['td', 'th'])
                    if len(cols) >= 2:
                        name = cols[0].get_text().strip().upper()
                        val_str = cols[1].get_text().strip()
                        clean_val = re.sub(r'[^\d]', '', val_str)
                        
                        if clean_val.isdigit() and len(clean_val) >= 4:
                            val = int(clean_val)
                            if 'RON 95' in name or 'RON95' in name:
                                prices["ron95_3"] = val
                                found_count += 1
                            elif 'E5' in name:
                                prices["e5_ron92"] = val
                                found_count += 1
                            elif 'DO' in name or 'DIESEL' in name:
                                prices["do_005s"] = val
                                found_count += 1
                                
            if found_count > 0:
                print(f"Vượt WAF thành công! Đã cào được {found_count} chỉ số trực tuyến từ PVOIL.")
            else:
                print("Không tìm thấy dữ liệu khớp trong HTML, giữ giá trị hiện hành.")
        else:
            print(f"Trang chính thống phản hồi mã lỗi: {response.status_code}, dùng giá trị dự phòng.")
            
    except Exception as e:
        print(f"Lỗi kết nối khi cào dữ liệu qua cloudscraper: {e}")

    # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (PVOIL Live Bypass)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = crawl_official_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
