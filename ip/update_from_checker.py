#!/usr/bin/env python3
import re

def parse_m3u_by_url(filename):
    """Parse M3U file and return dict with URL as key"""
    channels = {}
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                if url.startswith('http'):
                    channels[url] = {
                        'extinf_line': line,
                        'url': url
                    }
            i += 2
        else:
            i += 1
    
    return channels

def update_from_checker():
    # Parse both files
    checker_channels = parse_m3u_by_url('./iptv-checker-176.m3u')
    ship_channels = parse_m3u_by_url('./SHIPTV2026-7.m3u')
    
    # Read SHIPTV file content
    with open('./SHIPTV2026-7.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find header
    header = ""
    if lines[0].startswith('#EXTM3U'):
        header = lines[0]
    
    # Process channels
    updated_lines = []
    if header:
        updated_lines.append(header)
    
    removed_count = 0
    updated_count = 0
    kept_count = 0
    
    i = 1 if header else 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                
                if url.startswith('http'):
                    if url in checker_channels:
                        # URL exists in checker file - keep/update channel info
                        checker_extinf = checker_channels[url]['extinf_line']
                        
                        if line != checker_extinf:
                            # Update with checker file info
                            updated_lines.append(checker_extinf + '\n')
                            updated_lines.append(lines[i + 1])
                            updated_count += 1
                            
                            # Extract channel names for logging
                            ship_name = re.search(r'tvg-name="([^"]*)"', line)
                            checker_name = re.search(r'tvg-name="([^"]*)"', checker_extinf)
                            ship_name = ship_name.group(1) if ship_name else "Unknown"
                            checker_name = checker_name.group(1) if checker_name else "Unknown"
                            print(f"Updated: {ship_name} -> {checker_name}")
                        else:
                            # Keep original
                            updated_lines.append(lines[i])
                            updated_lines.append(lines[i + 1])
                            kept_count += 1
                    else:
                        # URL not in checker file - remove
                        removed_count += 1
                        name_match = re.search(r'tvg-name="([^"]*)"', line)
                        channel_name = name_match.group(1) if name_match else "Unknown"
                        print(f"Removed: {channel_name}")
                else:
                    # Non-http URL - keep as is
                    updated_lines.append(lines[i])
                    updated_lines.append(lines[i + 1])
            else:
                # EXTINF without URL - keep
                updated_lines.append(lines[i])
            i += 2
        elif line.startswith('#') and '==========' in line:
            # Group comment - keep
            updated_lines.append(lines[i])
            i += 1
        elif line == '':
            # Empty line - keep
            updated_lines.append(lines[i])
            i += 1
        else:
            # Other content - skip
            i += 1
    
    # Write to new file
    with open('./SHIPTV2026-8.m3u', 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print(f"\n文件更新完成:")
    print(f"保留频道: {kept_count}")
    print(f"更新频道信息: {updated_count}")
    print(f"删除频道: {removed_count}")
    print(f"总剩余频道: {kept_count + updated_count}")
    print("已创建新文件: SHIPTV2026-8.m3u")

if __name__ == "__main__":
    update_from_checker()
