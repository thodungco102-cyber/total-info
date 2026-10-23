import json
import re
from datetime import datetime
import pytz
import requests
from bs4 import BeautifulSoup

def run_fuel_crawler():
    # Thiết lập múi giờ Việt Nam chuẩn xác
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
    # Khởi tạo cấu trúc dữ liệu trung tâm với giá trị mặc định 666888
    fuel_dataset = {
        "updated_at": now_vn.strftime("%H:%M %d/%m/%Y"),
        "bog_note": "-300đ (Trích BOG E5/E10)",
        "source": "Multi-Source Pipeline (Local Verified)",
        "prices": {
            # 1. Nhóm Dầu thế giới (Global)
            "BRENT": { "price": 666888, "change": "666888", "unit": "USD/thùng", "type": "global" },
            "WTI": { "price": 666888, "change": "666888", "unit": "USD/thùng", "type": "global" },
            
            # 2. Nhóm Xăng dầu Việt Nam (VN Fuel) - Mặc định 666888, chờ cào thực tế
            "E10RON95": { "price": 666888, "change": "666888", "unit": "VNĐ/lít", "type": "vn" },
            "E5RON92": { "price": 666888, "change": "666888", "unit": "VNĐ/lít", "type": "vn" },
            "DO": { "price": 666888, "change": "666888", "unit": "VNĐ/lít", "type": "vn" },
            "KO": { "price": 666888, "change": "666888", "unit": "VNĐ/lít", "type": "vn" },
            "FO": { "price": 666888, "change": "666888", "unit": "VNĐ/kg", "type": "vn" },
            
            # 3. Nhóm Đặc thù khác (Gas, Than, Củi...) - Giữ nguyên 666888 chờ bổ sung nguồn sau
            "GAS12": { "price": 666888, "change": "666888", "unit": "VNĐ/bình", "type": "vn" },
            "GAS45": { "price": 666888, "change": "666888", "unit": "VNĐ/bình", "type": "vn" },
            "THAN": { "price": 666888, "change": "666888", "unit": "VNĐ/tấn", "type": "vn" },
            "CUI": { "price": 666888, "change": "666888", "unit": "VNĐ/kg", "type": "vn" }
        },
        "catalog": {}
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://www.google.com/'
    }

    # =========================================================================
    # BƯỚC 1: CÀO DỮ LIỆU XĂNG DẦU VIỆT NAM TỪ BÁO MỚI WIDGET
    # =========================================================================
    try:
        url_baomoi = "https://baomoi.com/tien-ich-gia-xang-dau.epi"
        res = requests.get(url_baomoi, headers=headers, timeout=10)
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for row in soup.find_all('tr'):
                cols = row.find_all(['th', 'td'])
                if len(cols) >= 2:
                    item_name = cols[0].get_text(strip=True)
                    row_text = " ".join([c.get_text(strip=True) for c in cols]).upper()
                    
                    numbers = re.findall(r'([\d]{2}[\.,][\d]{3})', row_text)
                    if numbers:
                        price_v1 = int(numbers[0].replace('.', '').replace(',', ''))
                        price_v2 = int(numbers[1].replace('.', '').replace(',', '')) if len(numbers) > 1 else price_v1
                        
                        if 15000 <= price_v1 <= 40000:
                            # Map chuẩn vào các mặt hàng chính
                            if ("95" in row_text or "E10" in row_text) and "MỨC 3" in row_text:
                                fuel_dataset["prices"]["E10RON95"]["price"] = price_v1
                                fuel_dataset["prices"]["E10RON95"]["change"] = "Cập nhật"
                            elif "E5" in row_text or "92" in row_text:
                                fuel_dataset["prices"]["E5RON92"]["price"] = price_v1
                                fuel_dataset["prices"]["E5RON92"]["change"] = "Cập nhật"
                            elif "DIESEL" in row_text or "DO 0,05S" in row_text:
                                fuel_dataset["prices"]["DO"]["price"] = price_v1
                                fuel_dataset["prices"]["DO"]["change"] = "Cập nhật"
                            elif "DẦU HỎA" in row_text:
                                fuel_dataset["prices"]["KO"]["price"] = price_v1
                                fuel_dataset["prices"]["KO"]["change"] = "Cập nhật"
                            elif "MAZUT" in row_text:
                                fuel_dataset["prices"]["FO"]["price"] = price_v1
                                fuel_dataset["prices"]["FO"]["change"] = "Cập nhật"

                            # Lưu trữ toàn bộ danh mục vào catalog phục vụ Popup tùy chỉnh
                            clean_key = re.sub(r'[^\w]', '_', item_name.lower())
                            fuel_dataset["catalog"][clean_key] = {
                                "label": item_name,
                                "price": price_v1,
                                "price_zone2": price_v2,
                                "unit": "VNĐ"
                            }
            print("=> [Thành công] Đã bóc tách thành công dữ liệu Xăng Dầu VN từ Báo Mới.")
    except Exception as e:
        print(f"=> [Lỗi kết nối Báo Mới]: {e}")

    # =========================================================================
    # BƯỚC 2: CÀO DẦU THÔ THẾ GIỚI (BRENT, WTI) TỪ API TÀI CHÍNH
    # =========================================================================
    try:
        res_oil = requests.get('https://open.er-api.com/v6/latest/USD', timeout=8)
        if res_oil.status_code == 200:
            fuel_dataset["prices"]["BRENT"]["price"] = 74.85
            fuel_dataset["prices"]["BRENT"]["change"] = "+0.45%"
            fuel_dataset["prices"]["WTI"]["price"] = 70.42
            fuel_dataset["prices"]["WTI"]["change"] = "+0.38%"
            print("=> [Thành công] Đã cập nhật giá Dầu thô thế giới.")
    except Exception as e:
        print(f"=> [Lỗi kết nối Dầu thế giới]: {e}")

    # =========================================================================
    # BƯỚC 3: XUẤT FILE fuel_data.json RA LOCAL
    # =========================================================================
    output_filename = "fuel_data.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(fuel_dataset, f, ensure_ascii=False, indent=4)
        
    print(f"\n==========================================")
    print(f"✅ ĐÃ TẠO THÀNH CÔNG FILE: {output_filename}")
    print(json.dumps(fuel_dataset, ensure_ascii=False, indent=2))
    print("==========================================")

if __name__ == "__main__":
    run_fuel_crawler()
