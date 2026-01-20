#!/usr/bin/env python3
import re

def get_urls_from_m3u(filename):
    """Extract all URLs from M3U file"""
    urls = set()
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if line.startswith('http'):
            urls.add(line)
    
    return urls

def filter_by_checker():
    # Get URLs from checker file
    checker_urls = get_urls_from_m3u('./iptv-checker-176.m3u')
    
    # Read SHIPTV file
    with open('./SHIPTV2026-7.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Filter channels
    filtered_lines = []
    removed_count = 0
    kept_count = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                
                if url.startswith('http'):
                    if url in checker_urls:
                        # Keep channel
                        filtered_lines.append(lines[i])
                        filtered_lines.append(lines[i + 1])
                        kept_count += 1
                    else:
                        # Remove channel
                        removed_count += 1
                        name_match = re.search(r'tvg-name="([^"]*)"', line)
                        channel_name = name_match.group(1) if name_match else "Unknown"
                        print(f"Removed: {channel_name}")
                else:
                    # Non-http URL - keep
                    filtered_lines.append(lines[i])
                    filtered_lines.append(lines[i + 1])
            else:
                # EXTINF without URL - keep
                filtered_lines.append(lines[i])
            i += 2
        else:
            # Keep headers, comments, empty lines
            filtered_lines.append(lines[i])
            i += 1
    
    # Write filtered file
    with open('./SHIPTV2026-9.m3u', 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)
    
    print(f"\n文件过滤完成:")
    print(f"保留频道: {kept_count}")
    print(f"删除频道: {removed_count}")
    print("已创建新文件: SHIPTV2026-9.m3u")

if __name__ == "__main__":
    filter_by_checker()
