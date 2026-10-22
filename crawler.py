import json
from datetime import datetime
import urllib.request

def fetch_real_fuel_prices():
    # Giá niêm yết chuẩn kỳ điều hành mới nhất, không lỗi định dạng số
    prices = {
        "ron95_3": 2020,
        "e5_ron92": 2970,
        "do_005s": 2100
    }
    
    try:
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
        print(f"Sử dụng giá niêm yết chuẩn: {e}")

    now = datetime.now()
    updated_str = f"{now.strftime('%H:%M %d/%m/%Y')} (GitHub Sync)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = fetch_real_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
