#!/usr/bin/env python3
import re

def find_duplicates():
    channels = {}
    duplicates = []
    
    with open('./SHIPTV2026.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Extract channel name
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            if name_match:
                channel_name = name_match.group(1)
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith('http'):
                        key = f"{channel_name}|{url}"
                        if key in channels:
                            duplicates.append({
                                'name': channel_name,
                                'url': url,
                                'first_line': channels[key],
                                'duplicate_line': i + 1
                            })
                        else:
                            channels[key] = i + 1
            i += 2
        else:
            i += 1
    
    # Also check for same name with different URLs
    name_urls = {}
    for key in channels:
        name, url = key.split('|', 1)
        if name in name_urls:
            name_urls[name].append(url)
        else:
            name_urls[name] = [url]
    
    print("=== 完全重复的条目 (频道名和URL都相同) ===")
    if duplicates:
        for dup in duplicates:
            print(f"频道: {dup['name']}")
            print(f"URL: {dup['url']}")
            print(f"首次出现行: {dup['first_line']}, 重复出现行: {dup['duplicate_line']}")
            print("-" * 50)
    else:
        print("未发现完全重复的条目")
    
    print("\n=== 频道名相同但URL不同的条目 ===")
    same_name_diff_url = []
    for name, urls in name_urls.items():
        if len(urls) > 1:
            same_name_diff_url.append((name, urls))
    
    if same_name_diff_url:
        for name, urls in same_name_diff_url:
            print(f"频道名: {name}")
            for i, url in enumerate(urls, 1):
                print(f"  URL {i}: {url}")
            print("-" * 50)
    else:
        print("未发现频道名相同但URL不同的条目")
    
    print(f"\n总结:")
    print(f"完全重复条目: {len(duplicates)}")
    print(f"频道名重复但URL不同: {len(same_name_diff_url)}")

if __name__ == "__main__":
    find_duplicates()
