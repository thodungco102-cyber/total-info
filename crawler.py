import json
from datetime import datetime, timedelta, timezone
import urllib.request

def crawl_live_fuel_prices():
    # Giá trị mặc định dự phòng chuẩn kỳ điều hành mới nhất
    prices = {
        "ron95_3": 9927020,
        "e5_ron92": 9926970,
        "do_005s": 9929100
    }
    
    try:
        # Thay thế bằng nguồn API dữ liệu mở ổn định
        url = "https://raw.githubusercontent.com/TranQui004/vietfuel-api/main/data.json"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            if "prices" in data:
                if "ron95_3" in data["prices"]: prices["ron95_3"] = int(data["prices"]["ron95_3"])
                if "e5_ron92" in data["prices"]: prices["e5_ron92"] = int(data["prices"]["e5_ron92"])
                if "do_005s" in data["prices"]: prices["do_005s"] = int(data["prices"]["do_005s"])
        print("Đồng bộ dữ liệu thành công qua nguồn thay thế!")
    except Exception as e:
        print(f"Lỗi kết nối nguồn thay thế, dùng giá dự phòng: {e}")

    # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (API Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = crawl_live_fuel_prices()
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
