import requests

#url = "https://api.lodgify.com/v2/properties"
#api_key = '4PE72MIUggANayatgtL7crI9SyEMllqE25DERi/2+Ue/GnmRXyMjqnsyc61u/frt'

#headers = {
#    "Accept": "application/json",   
#    "X-ApiKey": api_key             
#}

import requests

url = "https://us-real-estate-listings.p.rapidapi.com/v2/property"

headers = {
	"x-rapidapi-key": "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
	"x-rapidapi-host": "us-real-estate-listings.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

# always print status and any returned headers for debugging
print("Status:", response.status_code)
print("Response headers:", response.headers)

if response.ok:
    data = response.json()
    print("Data:", data)
else:
    print("Error:", response.status_code, response.text)