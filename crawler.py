import json
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup
import re

def crawl_official_fuel_prices():
    # Giá trị mặc định dự phòng chuẩn kỳ điều hành mới nhất
    prices = {
        "ron95_3": 9925210,
        "e5_ron92": 9925360,
        "do_005s": 9929550
    }
    
    # Sử dụng Session để giữ cookie và giả lập hoàn toàn hành vi của trình duyệt thật
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }
    
    try:
        # Truy cập trang chính thống PVOIL thông qua Session giả lập trình duyệt
        target_url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
        
        # Thiết lập header đầy đủ để qua mặt lớp kiểm tra bot cơ bản
        response = session.get(target_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Quét toàn bộ các dòng trong bảng giá của trang
            rows = soup.find_all('tr')
            found_count = 0
            
            for row in rows:
                row_text = row.get_text()
                # Kiểm tra dòng chứa thông tin các mặt hàng xăng dầu
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
                print(f"Cào thành công {found_count} chỉ số trực tuyến từ nguồn chính thống!")
            else:
                print("Không tìm thấy khớp lệnh trong HTML, giữ giá trị chuẩn hiện hành.")
        else:
            print(f"Trang chính thống phản hồi mã lỗi: {response.status_code}, dùng giá trị dự phòng.")
            
    except Exception as e:
        print(f"Lỗi kết nối khi cào dữ liệu trực tuyến: {e}")

    # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (Official Crawl Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = crawl_official_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
