#!/usr/bin/env python3

import requests
from urllib.parse import quote

def test_osm_search(location):
    """測試 OpenStreetMap 搜尋功能"""
    encoded_name = quote(location)
    search_url = f'https://nominatim.openstreetmap.org/search?format=json&q={encoded_name}&limit=3'
    
    print(f'搜尋: {location}')
    print(f'URL: {search_url}')
    
    try:
        response = requests.get(search_url, timeout=10)
        if response.status_code == 200:
            results = response.json()
            print(f'找到 {len(results)} 個結果:')
            
            for i, result in enumerate(results):
                display_name = result.get('display_name', 'N/A')
                osm_type = result.get('osm_type')
                osm_id = result.get('osm_id')
                
                print(f'  {i+1}. {display_name}')
                print(f'     Type: {osm_type}, ID: {osm_id}')
                
                if osm_type and osm_id:
                    link = f'https://www.openstreetmap.org/{osm_type}/{osm_id}'
                    print(f'     Link: {link}')
                print()
        else:
            print(f'HTTP 錯誤: {response.status_code}')
    except Exception as e:
        print(f'請求錯誤: {e}')

if __name__ == '__main__':
    # 測試幾個地點
    test_osm_search('台灣')
    print('-' * 50)
    test_osm_search('台北市')
    print('-' * 50)
    test_osm_search('中正紀念堂')
