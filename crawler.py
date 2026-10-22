import json
from datetime import datetime, timedelta, timezone
import urllib.request

def fetch_live_fuel_data():
    # Endpoint API công khai hoặc nguồn dữ liệu mở cung cấp giá nhiên liệu thực tế
    api_url = "https://api.jsonserver.io/fuel-prices-vn"
    
    req = urllib.request.Request(
        api_url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    # Thực hiện gọi mạng lấy dữ liệu sống
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        return data

if __name__ == "__main__":
    try:
        # Lấy dữ liệu trực tuyến từ nguồn ngoài
        external_data = fetch_live_fuel_data()
        
        # Đồng bộ chuẩn giờ Việt Nam (GMT+7)
        vn_tz = timezone(timedelta(hours=7))
        now_vn = datetime.now(vn_tz)
        updated_str = f"{now_vn.strftime('%H:%M %d/%m/%Y')} (API Live Sync)"

        fuel_data = {
            "updated_at": updated_str,
            "prices": external_data.get("prices", {})
        }
        
        # Ghi đè vào file fuel_data.json để đẩy lên GitHub Raw
        with open("fuel_data.json", "w", encoding="utf-8") as f:
            json.dump(fuel_data, f, ensure_ascii=False, indent=4)
            
        print("Đã fetch và cập nhật dữ liệu trực tuyến thành công từ nguồn ngoài!")
        
    except Exception as e:
        # Nếu lỗi mạng hoặc API chết, văng lỗi để GitHub Actions báo đỏ, 
        # tuyệt đối không dùng số ảo che đậy để đảm bảo tính chính xác của dữ liệu
        print(f"Lỗi kết nối trực tuyến: {e}")
        raise e
