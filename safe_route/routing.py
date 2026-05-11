import time
import requests
import re
import mysql.connector

# Your database configuration
DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',
    'database': 'iteration_1',
}

def clean_address_for_search(address):
    """
    Smart address cleaning:
    Converts "Carlton Baths, 216-248 Rathdowne Street, CARLTON VIC 3053"
    to "216 Rathdowne Street, CARLTON, Victoria"
    """
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 2:
        street = parts[-2]
        suburb_info = parts[-1]
        
        # Simplify address ranges (216-248) to the starting number (216) for better map engine recognition
        street = re.sub(r'^(\d+)-\d+', r'\1', street)
        
        # Replace abbreviation VIC with the full name Victoria to improve hit rate
        suburb_info = suburb_info.replace("VIC", "Victoria")
        
        return f"{street}, {suburb_info}, Australia"
    return f"{address}, Australia"

def geocode_address(address):
    """Use the more lenient Photon (Komoot) API for querying and add strict browser spoofing"""
    url = "https://photon.komoot.io/api/"
    
    # !!! This was the missing step !!! Perfectly spoof a real Chrome browser visit
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    # Strategy 1: Precise street-level search after cleaning
    query1 = clean_address_for_search(address)
    
    # Strategy 2: If the street number is too obscure, step back and search only "Street Name + Suburb"
    query2_parts = query1.split(',')
    query2 = f"{re.sub(r'^\d+\s*', '', query2_parts[0])}, {query2_parts[1]}, Australia" if len(query2_parts) >= 2 else query1

    for q in [query1, query2]:
        try:
            params = {'q': q, 'limit': 1}
            # This time, bring the headers spoofing mask!
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 429:
                print(f"  -> ⚠️ Rate limited by API! Waiting 5 seconds before continuing...")
                time.sleep(5)
                continue
            elif resp.status_code != 200:
                print(f"  -> ❌ API error: HTTP {resp.status_code}")
                continue

            data = resp.json()
            if 'features' in data and len(data['features']) > 0:
                # Photon returns coordinates in [Longitude, Latitude] format
                lon, lat = data['features'][0]['geometry']['coordinates']
                return lat, lon
                
        except requests.exceptions.Timeout:
            print("  -> ⏱️ Request timeout")
        except Exception as e:
            print(f"  -> ❌ Exception occurred: {e}")
            
        time.sleep(1.2) # Respect the API, pause briefly

    return None, None

def main():
    print("Connecting to database...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    print("\nFinding building sites that need coordinate conversion...")
    # Only find data that hasn't gotten coordinates yet, resume from where it left off last time
    cursor.execute("""
        SELECT address 
        FROM building_permits 
        WHERE lat IS NULL OR lon IS NULL
    """)
    records = cursor.fetchall()
    print(f"Found {len(records)} addresses to convert.")

    success_count = 0
    for i, row in enumerate(records):
        address = row['address']
        print(f"[{i+1}/{len(records)}] Converting: {address[:60]}...")
        
        lat, lon = geocode_address(address)
        
        if lat and lon:
            update_cursor = conn.cursor()
            update_cursor.execute("""
                UPDATE building_permits 
                SET lat = %s, lon = %s 
                WHERE address = %s
            """, (lat, lon, address))
            conn.commit()
            update_cursor.close()
            success_count += 1
            print(f"  -> ✅ Success: {lat}, {lon}")
        else:
            print("  -> ⏭️ Abandoning this address, skipping")

    cursor.close()
    conn.close()
    print(f"\n🎉 Run complete! Successfully updated coordinates for {success_count} building sites this time.")

if __name__ == "__main__":
    main()