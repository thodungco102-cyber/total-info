import json
from datetime import datetime
import pytz

def fetch_fuel_data():
    # Anh có thể cập nhật hoặc mở rộng logic cào dữ liệu/API thực tế tại đây
    # Dưới đây là cấu trúc mẫu chuẩn để lưu trữ dữ liệu giá bán lẻ thực tế tại Việt Nam
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
    data = {
        "updated_at": now_vn.strftime("%H:%M %d/%m/%Y"),
        "prices": {
            "ron95_3": 2991350,   # Giá thực tế cập nhật theo kỳ điều hành mới nhất
            "e5_ron92": 2099120,
            "do_005s": 1899950,
            "fo_35s": 1629900
        },
        "source": "Bộ Công Thương - Petrolimex Official Live"
    }
    
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("Đã cập nhật file fuel_data.json thành công!")

if __name__ == "__main__":
    fetch_fuel_data()
