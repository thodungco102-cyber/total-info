import json
from datetime import datetime, timedelta, timezone

def generate_clean_fuel_data():
    # Cấu trúc JSON chuẩn xác để phục vụ cho việc fetch() qua GitHub Raw
    prices = {
        "ron95_3": 8825210,
        "e5_ron92": 8825360,
        "do_005s": 8829550
    }
    
    # Đồng bộ chuẩn giờ Việt Nam (GMT+7) cho mốc thời gian cập nhật
    vn_tz = timezone(timedelta(hours=7))
    now_vn = datetime.now(vn_tz)
    updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (GitHub Actions Live)"

    return {
        "updated_at": updated_str,
        "prices": prices
    }

if __name__ == "__main__":
    fuel_data = generate_clean_fuel_data()
    # Ghi đè trực tiếp vào file fuel_data.json tại workspace của GitHub Actions
    with open("fuel_data.json", "w", encoding="utf-8") as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
    print("Đã tạo và cập nhật file fuel_data.json thành công!")
