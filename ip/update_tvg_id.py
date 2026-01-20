#!/usr/bin/env python3
import re

def parse_tvg_ids(filename):
    """Parse M3U file and return dict with channel name as key and tvg-id as value"""
    channels = {}
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        if line.startswith('#EXTINF:'):
            # Extract channel name and tvg-id
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            id_match = re.search(r'tvg-id="([^"]*)"', line)
            
            if name_match:
                channel_name = name_match.group(1)
                tvg_id = id_match.group(1) if id_match else ""
                channels[channel_name] = tvg_id
    
    return channels

def update_tvg_ids():
    # Parse IPTV file for reference tvg-ids
    iptv_ids = parse_tvg_ids('./IPTV20251019.m3u')
    
    # Read SHIPTV file
    with open('./SHIPTV2026-3.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    updated_count = 0
    created_count = 0
    
    for i, line in enumerate(lines):
        if line.startswith('#EXTINF:'):
            # Extract current channel name and tvg-id
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            
            if name_match:
                channel_name = name_match.group(1)
                
                if channel_name in iptv_ids:
                    new_tvg_id = iptv_ids[channel_name]
                    
                    # Check if tvg-id exists in current line
                    id_match = re.search(r'tvg-id="([^"]*)"', line)
                    
                    if id_match:
                        current_tvg_id = id_match.group(1)
                        if current_tvg_id != new_tvg_id:
                            # Update existing tvg-id
                            new_line = re.sub(r'tvg-id="[^"]*"', f'tvg-id="{new_tvg_id}"', line)
                            lines[i] = new_line
                            updated_count += 1
                            print(f"Updated {channel_name}: tvg-id '{current_tvg_id}' -> '{new_tvg_id}'")
                    else:
                        # Add new tvg-id (insert after #EXTINF:-1)
                        new_line = line.replace('#EXTINF:-1 ', f'#EXTINF:-1 tvg-id="{new_tvg_id}" ')
                        lines[i] = new_line
                        created_count += 1
                        print(f"Added tvg-id for {channel_name}: '{new_tvg_id}'")
    
    # Write to new file
    with open('./SHIPTV2026-4.m3u', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\ntvg-id更新完成:")
    print(f"更新现有tvg-id: {updated_count}")
    print(f"新增tvg-id: {created_count}")
    print("已创建新文件: SHIPTV2026-4.m3u")

if __name__ == "__main__":
    update_tvg_ids()
