#!/usr/bin/env python3
import re

def parse_m3u(filename):
    """Parse M3U file and return dict with channel name as key and URL as value"""
    channels = {}
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Extract channel name from tvg-name attribute
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            if name_match:
                channel_name = name_match.group(1)
                # Get the next line which should be the URL
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith('http'):
                        channels[channel_name] = {
                            'extinf_line': line,
                            'url': url,
                            'line_number': i
                        }
            i += 2
        else:
            i += 1
    
    return channels

def update_urls():
    # Parse both files
    iptv_channels = parse_m3u('./IPTV20251019.m3u')
    ship_channels = parse_m3u('./SHIPTV2026-1.m3u')
    
    # Read SHIPTV2026-1.m3u content
    with open('./SHIPTV2026-1.m3u', 'r', encoding='utf-8') as f:
        content = f.readlines()
    
    updated_count = 0
    
    # Find matching channel names and update URLs
    for channel_name in ship_channels:
        if channel_name in iptv_channels:
            ship_url = ship_channels[channel_name]['url']
            iptv_url = iptv_channels[channel_name]['url']
            
            if ship_url != iptv_url:
                # Find the URL line in content and update it
                line_num = ship_channels[channel_name]['line_number'] + 1
                if line_num < len(content):
                    content[line_num] = iptv_url + '\n'
                    updated_count += 1
                    print(f"Updated {channel_name}: {ship_url} -> {iptv_url}")
    
    # Write to new file
    with open('./SHIPTV2026-2.m3u', 'w', encoding='utf-8') as f:
        f.writelines(content)
    
    print(f"\n更新完成:")
    print(f"总更新频道数: {updated_count}")
    print("已创建新文件: SHIPTV2026-2.m3u")

if __name__ == "__main__":
    update_urls()
