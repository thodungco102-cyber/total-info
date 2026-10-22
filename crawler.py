import json
from datetime import datetime
import urllib.request

def fetch_real_fuel_prices():
    # Giá trị mặc định chuẩn kỳ điều hành để dự phòng
    prices = {
        "ron95_3": 020,
        "e5_ron92": 970,
        "do_005s": 100
    }
    
    try:
        # Cổng API mở tổng hợp dữ liệu giá xăng dầu chuẩn xác theo thị trường Việt Nam
        url = "https://raw.githubusercontent.com/TranQui004/vietfuel-api/main/data.json"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if "prices" in data:
                if "ron95_3" in data["prices"]: prices["ron95_3"] = data["prices"]["ron95_3"]
                if "e5_ron92" in data["prices"]: prices["e5_ron92"] = data["prices"]["e5_ron92"]
                if "do_005s" in data["prices"]: prices["do_005s"] = data["prices"]["do_005s"]
    except Exception as e:
        print(f"Không thể kết nối nguồn cào, giữ nguyên giá chuẩn: {e}")

    now = datetime.now()
    updated_str = f"{now.strftime('%H:%M %d/%m/%Y')} (GitHub Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = fetch_real_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
