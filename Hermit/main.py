import requests

url = "https://api.lodgify.com/v2/properties"

api_key = '4PE72MIUggANayatgtL7crI9SyEMllqE25DERi/2+Ue/GnmRXyMjqnsyc61u/frt'

headers = {
    "X-ApiKey": api_key
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # 200 means data request successful
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}, {response.text}")