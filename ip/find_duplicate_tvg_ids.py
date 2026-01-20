#!/usr/bin/env python3
import re

def find_duplicate_tvg_ids():
    tvg_id_lines = {}
    
    with open('./SHIPTV2026-4.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line_num, line in enumerate(lines, 1):
        if line.startswith('#EXTINF:'):
            # Extract tvg-id and channel name
            id_match = re.search(r'tvg-id="([^"]*)"', line)
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            
            if id_match:
                tvg_id = id_match.group(1)
                channel_name = name_match.group(1) if name_match else "Unknown"
                
                if tvg_id in tvg_id_lines:
                    tvg_id_lines[tvg_id].append((line_num, channel_name))
                else:
                    tvg_id_lines[tvg_id] = [(line_num, channel_name)]
    
    # Find duplicates
    duplicates = {tvg_id: entries for tvg_id, entries in tvg_id_lines.items() if len(entries) > 1}
    
    print("=== 重复的tvg-id值 ===")
    
    if duplicates:
        for tvg_id, entries in sorted(duplicates.items()):
            print(f"\ntvg-id=\"{tvg_id}\" (共{len(entries)}个):")
            for line_num, channel_name in entries:
                print(f"  行 {line_num}: {channel_name}")
    else:
        print("未发现重复的tvg-id值")
    
    print(f"\n总计:")
    print(f"唯一tvg-id数量: {len(tvg_id_lines)}")
    print(f"重复tvg-id数量: {len(duplicates)}")
    total_duplicates = sum(len(entries) - 1 for entries in duplicates.values())
    print(f"重复条目总数: {total_duplicates}")

if __name__ == "__main__":
    find_duplicate_tvg_ids()
