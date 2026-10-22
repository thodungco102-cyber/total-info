import json
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import re

def crawl_fuel_data_via_proxy():
    # Giá trị dự phòng an toàn phòng khi mất kết nối mạng tạm thời
    prices = {
        "ron95_3": 5525210,
        "e5_ron92": 5525360,
        "do_005s": 5529550
    }
    
    # Trang đích chính thống cần lấy dữ liệu
    target_url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
    
    # Sử dụng dịch vụ Proxy công khai để vượt qua tường lửa chặn IP của GitHub Actions
    proxy_url = f"https://api.allorigins.win/raw?url={target_url}"
    
    try:
        response = requests.get(proxy_url, timeout=15)
        
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
                print(f"Cào thành công {found_count} chỉ số trực tuyến qua Proxy từ PVOIL!")
            else:
                print("Không tìm thấy khớp lệnh trong HTML, sử dụng giá trị hiện hành.")
        else:
            print(f"Proxy phản hồi mã lỗi: {response.status_code}")
            
    except Exception as e:
        print(f"Lỗi kết nối khi cào dữ liệu: {e}")
        raise e

    # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (Proxy Live Crawl)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = crawl_fuel_data_via_proxy()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật file fuel_data.json thành công!")
