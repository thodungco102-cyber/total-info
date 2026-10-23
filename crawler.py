import json
import re
from datetime import datetime
import pytz
import requests
import xml.etree.ElementTree as ET

def fetch_fuel_from_rss_and_news():
    tz_vn = pytz.timezone('Asia/Ho_Chi_Minh')
    now_vn = datetime.now(tz_vn)
    
    fuel_data = {
        "updated_at": now_vn.strftime("%H:%M %d/%m/%Y"),
        "prices": {
            "ron95_3": 666888,
            "e5_ron92": 666888,
            "do_005s": 666888,
            "fo_35s": 666888
        },
        "source": "Fetch Error (666888)"
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    # =========================================================================
    # NGUỒN 1: BÓC TÁCH RSS BÁO KINH TẾ / BÁO LAO ĐỘNG / VNEXPRESS
    # =========================================================================
    rss_urls = [
        "https://laodong.vn/rss/kinh-te.rss",
        "https://vnexpress.net/rss/kinh-doanh.rss",
        "https://tuoitre.vn/rss/kinh-doanh.rss"
    ]

    fetched = False

    for url in rss_urls:
        if fetched: break
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code == 200:
                # Đọc XML RSS
                root = ET.fromstring(res.content)
                for item in root.findall('.//item'):
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    content = f"{title} {desc}"

                    # Nếu bài viết nói về điều hành giá xăng dầu
                    if any(k in content.lower() for k in ["giá xăng", "petrolimex", "ron 95", "e5 ron 92"]):
                        # RegEx bóc tách các con số giá thực tế (VD: 21.350 đồng/lít hoặc 21350)
                        ron_m = re.search(r'RON\s*95[^\d]*([\d\.]{5,6})', content, re.I)
                        e5_m = re.search(r'E5[^\d]*([\d\.]{5,6})', content, re.I)
                        do_m = re.search(r'dầu\s*diesel[^\d]*([\d\.]{5,6})', content, re.I)

                        if ron_m:
                            val = int(ron_m.group(1).replace('.', ''))
                            if 15000 <= val <= 35000: fuel_data["prices"]["ron95_3"] = val; fetched = True
                        if e5_m:
                            val = int(e5_m.group(1).replace('.', ''))
                            if 15000 <= val <= 35000: fuel_data["prices"]["e5_ron92"] = val; fetched = True
                        if do_m:
                            val = int(do_m.group(1).replace('.', ''))
                            if 15000 <= val <= 35000: fuel_data["prices"]["do_005s"] = val; fetched = True

                        if fetched:
                            fuel_data["source"] = f"RSS News Live ({url.split('/')[2]})"
                            print(f"=> [Thành công] Bóc tách giá từ RSS: {url}")
                            break
        except Exception as e:
            print(f"Lỗi đọc RSS {url}: {e}")

    # =========================================================================
    # NGUỒN 2: BÓC TÁCH TRỰC TIẾP TỪ TRANG THỊ TRƯỜNG BÁO CHÍ (FALLBACK)
    # =========================================================================
    if not fetched:
        try:
            # Quét trang tin tức tổng hợp giá thị trường
            news_res = requests.get("https://vietnamnet.vn/kinh-doanh/thi-truong", headers=headers, timeout=8)
            if news_res.status_code == 200:
                html = news_res.text
                ron_m = re.search(r'RON\s*95-III[^\d]*([\d\.]{5,6})', html, re.I)
                e5_m = re.search(r'E5\s*RON\s*92[^\d]*([\d\.]{5,6})', html, re.I)
                do_m = re.search(r'dầu\s*diesel[^\d]*([\d\.]{5,6})', html, re.I)

                if ron_m: fuel_data["prices"]["ron95_3"] = int(ron_m.group(1).replace('.', ''))
                if e5_m: fuel_data["prices"]["e5_ron92"] = int(e5_m.group(1).replace('.', ''))
                if do_m: fuel_data["prices"]["do_005s"] = int(do_m.group(1).replace('.', ''))

                if fuel_data["prices"]["ron95_3"] != 666888:
                    fuel_data["source"] = "VietNamNet Market Live"
                    fetched = True
                    print("=> [Thành công] Bóc tách từ VietNamNet Market!")
        except Exception as e:
            print(f"Lỗi đọc tin tức: {e}")

    # Ghi kết quả ra file JSON
    with open('fuel_data.json', 'w', encoding='utf-8') as f:
        json.dump(fuel_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n===> KẾT QUẢ CUỐI CÙNG:\n{json.dumps(fuel_data, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    fetch_fuel_from_rss_and_news()
