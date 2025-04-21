import requests

# ----------------------------------------
# 1) Lodgify code
#url = "https://api.lodgify.com/v2/properties"
#api_key = '4PE72MIUggANayatgtL7crI9SyEMllqE25DERi/2+Ue/GnmRXyMjqnsyc61u/frt'
#headers = {
#    "Accept": "application/json",   
#    "X-ApiKey": api_key             
#}
# ----------------------------------------

# 2) Our new RapidAPI search for rentals
RENT_URL = "https://us-real-estate-listings.p.rapidapi.com/for-rent"
rent_params = {
    "location": "Metairie, LA",  # change to desired city/ZIP
    "limit": 5,
    "offset": 0
}

# 3) Headers (Maro’s key)
headers = {
    "X-RapidAPI-Key":  "bfb6821e53msh848033d27b1e2d1p186d09jsnb3bc129f7ecb",
    "X-RapidAPI-Host": "us-real-estate-listings.p.rapidapi.com"
}

# 4) Fetch and print the rental listings
resp = requests.get(RENT_URL, headers=headers, params=rent_params)
resp.raise_for_status()
rent_listings = resp.json().get("listings", [])

print("=== Rental Listings (/for-rent) ===")
for lst in rent_listings:
    pid  = lst["property_id"]
    href = lst["href"]
    addr = lst["location"]["address"]
    print(f"ID:      {pid}")
    print(f"URL:     {href}")
    print(f"Address: {addr['line']}, {addr['city']}, {addr['state_code']} {addr['postal_code']}")
    print("-" * 40)

if not rent_listings:
    print("No rentals found; check your location/params.")
    exit(0)

# ----------------------------------------
# 5) Group’s original v2/property call, now with a real property_id
DETAIL_URL = "https://us-real-estate-listings.p.rapidapi.com/v2/property"
first_id    = rent_listings[0]["property_id"]
detail_params = {"property_id": first_id}

detail_resp = requests.get(DETAIL_URL, headers=headers, params=detail_params)
print("\n=== Detail View (/v2/property) ===")
print("Status:", detail_resp.status_code)
print("Response headers:", detail_resp.headers)

if detail_resp.ok:
    detail = detail_resp.json().get("listing") or detail_resp.json().get("data") or {}
    print("Detail for property ID:", first_id)
    print("URL:    ", detail.get("href") or detail.get("permalink"))
    addr = detail.get("location", {}).get("address", {})
    print("Address:", f"{addr.get('line')}, {addr.get('city')}, {addr.get('state_code')} {addr.get('postal_code')}")
else:
    print("Error fetching detail:", detail_resp.status_code, detail_resp.text)
