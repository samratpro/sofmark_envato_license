import requests

headers = {"Authorization": "Bearer ZjE15GJrDclwNQ7m8IssNtWolKimc0St"}
purchase_code = "86781236-23d0-4b3c-7dfa-c1c147e0dece"  # This is a sample

response = requests.get(
    f"https://api.envato.com/v3/market/author/sale?code={purchase_code}",
    headers=headers
)
print(response.status_code)
print(response.json())
if response.status_code == 200:
    print("✅ Valid Purchase")
    print(response.json())
else:
    print("❌ Invalid or Not Found")
