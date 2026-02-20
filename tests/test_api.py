import requests
import json

url = "http://127.0.0.1:8000/api/v1/search/hybrid"

# O kaybetme dediğim güvenlik anahtarın
headers = {
    "X-API-Key": "EKqU5PjulvYpaATOyzYBZooKHQoY3U7YdFG4fQOp1a8",
    "Content-Type": "application/json"
}

# Sorgumuz
payload = {
    "query": "denize sıfır, spa merkezi olan lüks bir otel arıyorum.",
    "city": "antalya",
    "limit": 3
}

print("Arama yapılıyor, güvenlik duvarı geçiliyor...")

response = requests.post(url, headers=headers, json=payload)

print(f"\nDurum Kodu: {response.status_code}")
print("Yanıt:")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))