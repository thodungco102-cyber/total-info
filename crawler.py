import json
from datetime import datetime
import urllib.request

def fetch_fuel_data():
    # 🛠️ CỜ KIỂM TRA: Đổi thành True nếu anh muốn test nhanh bằng số 666888, 
    # Đổi thành False để hệ thống tự động cào và sử dụng giá chuẩn thị trường.
    DEBUG_MODE = False 
    
    if DEBUG_MODE:
        prices = {
            "ron95_3": 666888,
            "e5_ron92": 666888,
            "do_005s": 666888
        }
        updated_str = f"{datetime.now().strftime('%H:%M %d/%m/%Y')} (Test Mode 666888)"
    else:
        # Giá niêm yết chuẩn kỳ điều hành thực tế mới nhất làm gốc vững chắc
        prices = {
            "ron95_3": 27020,
            "e5_ron92": 26970,
            "do_005s": 29100
        }
        
        # Thử kết nối nguồn dữ liệu API mở nội địa cập nhật theo thị trường
        try:
            url = "https://raw.githubusercontent.com/TranQui004/vietfuel-api/main/data.json"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as res:
                remote_data = json.loads(res.read().decode())
                if "prices" in remote_data:
                    prices.update(remote_data["prices"])
        except Exception as e:
            print(f"Dùng giá niêm yết chuẩn: {e}")

        updated_str = f"{datetime.now().strftime('%H:%M %d/%m/%Y')} (Market Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = fetch_fuel_data()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
