#!/usr/bin/env python3

def parse_m3u(file_path):
    """Parse M3U file and return dict of URL -> channel_name"""
    url_to_name = {}
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Extract channel name (after last comma)
            if ',' in line:
                channel_name = line.split(',')[-1]
                # Get next line which should be the URL
                if i + 1 < len(lines):
                    url = lines[i + 1].strip()
                    if url.startswith('http'):
                        url_to_name[url] = channel_name
    
    return url_to_name

def read_m3u_with_structure(file_path):
    """Read M3U file preserving structure"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return lines

def main():
    # Parse both files
    checker_urls = parse_m3u('/home/mike/iptv/iptv-checker-176.m3u')
    ship_lines = read_m3u_with_structure('/home/mike/iptv/SHIPTV2026-9.m3u')
    
    # Find channels to move
    channels_to_move = []
    remaining_lines = []
    
    i = 0
    while i < len(ship_lines):
        line = ship_lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            # Get channel name and URL
            if ',' in line:
                ship_channel_name = line.split(',')[-1]
                # Get next line (URL)
                if i + 1 < len(ship_lines):
                    url_line = ship_lines[i + 1].strip()
                    
                    if url_line.startswith('http'):
                        # Check if URL exists in checker file with different name
                        if url_line in checker_urls:
                            checker_name = checker_urls[url_line]
                            if ship_channel_name != checker_name:
                                # Move this channel
                                channels_to_move.append(ship_lines[i])
                                channels_to_move.append(ship_lines[i + 1])
                                i += 2  # Skip both lines
                                continue
                
            # Keep this channel
            remaining_lines.append(ship_lines[i])
            if i + 1 < len(ship_lines):
                remaining_lines.append(ship_lines[i + 1])
                i += 2
            else:
                i += 1
        else:
            # Keep non-EXTINF lines
            remaining_lines.append(ship_lines[i])
            i += 1
    
    # Write updated file
    with open('/home/mike/iptv/SHIPTV2026-9.m3u', 'w', encoding='utf-8') as f:
        # Write remaining content
        for line in remaining_lines:
            f.write(line)
        
        # Add separator and moved channels
        if channels_to_move:
            f.write('\n# ========== 频道名称不一致的频道 ==========\n')
            for line in channels_to_move:
                f.write(line)
    
    print(f"移动了 {len(channels_to_move)//2} 个频道到文件末尾")

if __name__ == "__main__":
    main()
