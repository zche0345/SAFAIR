import time
import requests
import re
import mysql.connector

# 你的数据库配置
DB_CONFIG = {
    'host': 'database-1.c12yc2e8ut1l.ap-southeast-2.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'tptp1515',
    'database': 'iteration_1',
}

def clean_address_for_search(address):
    """
    智能清洗地址：
    把 "Carlton Baths, 216-248 Rathdowne Street, CARLTON VIC 3053"
    变成 "216 Rathdowne Street, CARLTON, Victoria"
    """
    parts = [p.strip() for p in address.split(',')]
    if len(parts) >= 2:
        street = parts[-2]
        suburb_info = parts[-1]
        
        # 把范围门牌号 (216-248) 简化为起始号 (216)，地图引擎更好识别
        street = re.sub(r'^(\d+)-\d+', r'\1', street)
        
        # 把缩写 VIC 替换为全称 Victoria，提高命中率
        suburb_info = suburb_info.replace("VIC", "Victoria")
        
        return f"{street}, {suburb_info}, Australia"
    return f"{address}, Australia"

def geocode_address(address):
    """使用更宽容的 Photon (Komoot) 接口进行查询，并加入严格的浏览器伪装"""
    url = "https://photon.komoot.io/api/"
    
    # ！！！就是漏了这一步！！！完美伪装成真实的 Chrome 浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json'
    }
    
    # 策略 1：清洗后的精准街道级搜索
    query1 = clean_address_for_search(address)
    
    # 策略 2：如果门牌号太偏门，退一步只搜“街道名 + 区”
    query2_parts = query1.split(',')
    query2 = f"{re.sub(r'^\d+\s*', '', query2_parts[0])}, {query2_parts[1]}, Australia" if len(query2_parts) >= 2 else query1

    for q in [query1, query2]:
        try:
            params = {'q': q, 'limit': 1}
            # 这次带上 headers 伪装面具！
            resp = requests.get(url, params=params, headers=headers, timeout=10)
            
            if resp.status_code == 429:
                print(f"  -> ⚠️ 被接口限流！等待 5 秒后继续...")
                time.sleep(5)
                continue
            elif resp.status_code != 200:
                print(f"  -> ❌ 接口报错: HTTP {resp.status_code}")
                continue

            data = resp.json()
            if 'features' in data and len(data['features']) > 0:
                # Photon 返回的坐标格式是 [经度, 纬度]
                lon, lat = data['features'][0]['geometry']['coordinates']
                return lat, lon
                
        except requests.exceptions.Timeout:
            print("  -> ⏱️ 请求超时")
        except Exception as e:
            print(f"  -> ❌ 发生异常: {e}")
            
        time.sleep(1.2) # 尊重接口，稍微停顿

    return None, None

def main():
    print("连接数据库...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    print("\n查找需要转换坐标的工地...")
    # 只查找还没拿到坐标的数据，上次断掉的地方接着跑
    cursor.execute("""
        SELECT address 
        FROM building_permits 
        WHERE lat IS NULL OR lon IS NULL
    """)
    records = cursor.fetchall()
    print(f"找到 {len(records)} 个需要转换的地址。")

    success_count = 0
    for i, row in enumerate(records):
        address = row['address']
        print(f"[{i+1}/{len(records)}] 正在转换: {address[:60]}...")
        
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
            print(f"  -> ✅ 成功: {lat}, {lon}")
        else:
            print("  -> ⏭️ 放弃该地址，跳过")

    cursor.close()
    conn.close()
    print(f"\n🎉 运行结束！本次成功更新了 {success_count} 个工地的坐标。")

if __name__ == "__main__":
    main()