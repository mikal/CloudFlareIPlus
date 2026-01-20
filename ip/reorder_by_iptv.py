#!/usr/bin/env python3

def parse_m3u_channels(file_path):
    """Parse M3U file and return list of (extinf_line, url_line) tuples"""
    channels = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = []
    i = 0
    # Get header lines
    while i < len(lines) and not lines[i].strip().startswith('#EXTINF:'):
        header.append(lines[i])
        i += 1
    
    # Parse channels
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf_line = lines[i]
            if i + 1 < len(lines):
                url_line = lines[i + 1]
                channels.append((extinf_line, url_line))
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    return header, channels

def get_url_from_line(url_line):
    """Extract URL from line"""
    return url_line.strip()

def main():
    # Parse both files
    ship_header, ship_channels = parse_m3u_channels('/home/mike/iptv/SHIPTV2026-9.m3u')
    iptv_header, iptv_channels = parse_m3u_channels('/home/mike/iptv/IPTV20251019.m3u')
    
    # Create URL to channel mapping for SHIP file
    ship_url_to_channel = {}
    for extinf, url in ship_channels:
        url_clean = get_url_from_line(url)
        if url_clean.startswith('http'):
            ship_url_to_channel[url_clean] = (extinf, url)
    
    # Reorder based on IPTV file order
    reordered_channels = []
    used_urls = set()
    
    # First, add channels in IPTV order if they exist in SHIP
    for extinf, url in iptv_channels:
        url_clean = get_url_from_line(url)
        if url_clean.startswith('http') and url_clean in ship_url_to_channel:
            reordered_channels.append(ship_url_to_channel[url_clean])
            used_urls.add(url_clean)
    
    # Then add remaining SHIP channels not in IPTV
    for extinf, url in ship_channels:
        url_clean = get_url_from_line(url)
        if url_clean.startswith('http') and url_clean not in used_urls:
            reordered_channels.append((extinf, url))
    
    # Write new file
    output_file = '/home/mike/iptv/SHIPTV2026-9-reordered.m3u'
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        for line in ship_header:
            f.write(line)
        
        # Write reordered channels
        for extinf, url in reordered_channels:
            f.write(extinf)
            f.write(url)
    
    print(f"已创建重新排序的文件: {output_file}")
    print(f"共处理 {len(reordered_channels)} 个频道")
    
    # Validate M3U format
    validate_m3u(output_file)

def validate_m3u(file_path):
    """Validate M3U file format"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    errors = []
    
    # Check header
    if not lines[0].strip().startswith('#EXTM3U'):
        errors.append("文件应以 #EXTM3U 开头")
    
    # Check channel format
    i = 1
    channel_count = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            channel_count += 1
            # Check if next line is URL
            if i + 1 >= len(lines):
                errors.append(f"第 {i+1} 行: #EXTINF 后缺少URL")
            else:
                next_line = lines[i + 1].strip()
                if not next_line.startswith('http'):
                    errors.append(f"第 {i+2} 行: 期望HTTP URL，实际为: {next_line[:50]}")
            i += 2
        elif line.startswith('#'):
            i += 1  # Skip other comments
        elif line.startswith('http'):
            errors.append(f"第 {i+1} 行: URL前缺少#EXTINF")
            i += 1
        else:
            if line:  # Skip empty lines
                errors.append(f"第 {i+1} 行: 未知格式: {line[:50]}")
            i += 1
    
    if errors:
        print("\nM3U格式检查发现问题:")
        for error in errors:
            print(f"  - {error}")
    else:
        print(f"\nM3U格式检查通过! 共 {channel_count} 个频道")

if __name__ == "__main__":
    main()
