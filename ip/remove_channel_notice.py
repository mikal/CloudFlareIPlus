#!/usr/bin/env python3
import re

def remove_channel_notice():
    cleaned_lines = []
    removed_count = 0
    
    with open('./SHIPTV2026-4.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Check if next line exists (URL)
            if i + 1 < len(lines):
                # Extract channel name
                name_match = re.search(r'tvg-name="([^"]*)"', line)
                channel_name = name_match.group(1) if name_match else ""
                
                # Check if channel name contains "频道通告"
                if "频道通告" in channel_name:
                    removed_count += 1
                    print(f"Removed: {channel_name}")
                    # Skip both EXTINF and URL lines
                    i += 2
                    continue
                else:
                    # Keep both EXTINF and URL lines
                    cleaned_lines.append(lines[i])
                    cleaned_lines.append(lines[i + 1])
            else:
                # Keep EXTINF line if no URL follows
                cleaned_lines.append(lines[i])
            i += 2
        else:
            # Keep header and other lines
            cleaned_lines.append(lines[i])
            i += 1
    
    # Write to new file
    with open('./SHIPTV2026-5.m3u', 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"\n清理完成:")
    print(f"移除频道通告数量: {removed_count}")
    print("已创建新文件: SHIPTV2026-5.m3u")

if __name__ == "__main__":
    remove_channel_notice()
