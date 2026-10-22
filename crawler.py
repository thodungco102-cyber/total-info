import json

# Ghi dữ liệu test là 666888 để kiểm chứng quá trình đồng bộ GitHub Raw
fuel_data = {
    "updated_at": "15:00 15/10/2026",
    "prices": {
        "ron95_3": 666888,
        "e5_ron92": 666888,
        "do_005s": 666888
    }
}

with open("fuel_data.json", "w", encoding="utf-8") as f:
    json.dump(fuel_data, f, ensure_ascii=False, indent=4)
