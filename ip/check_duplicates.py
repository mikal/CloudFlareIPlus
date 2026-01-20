#!/usr/bin/env python3

def check_duplicate_urls(file_path):
    """Check for duplicate HTTP URLs in M3U file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    url_to_channels = {}
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf_line = lines[i].strip()
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line.startswith('http'):
                    if url_line not in url_to_channels:
                        url_to_channels[url_line] = []
                    # Extract channel name
                    channel_name = extinf_line.split(',')[-1] if ',' in extinf_line else "未知频道"
                    url_to_channels[url_line].append(channel_name)
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    # Find duplicates
    duplicates = {url: channels for url, channels in url_to_channels.items() if len(channels) > 1}
    
    return duplicates, len(url_to_channels)

def main():
    file_path = '/home/mike/iptv/SHIPTV2026-10.m3u'
    duplicates, total_urls = check_duplicate_urls(file_path)
    
    print(f"检查文件: {file_path}")
    print(f"总共 {total_urls} 个唯一URL")
    
    if duplicates:
        print(f"\n发现 {len(duplicates)} 个重复的URL:")
        for i, (url, channels) in enumerate(duplicates.items(), 1):
            print(f"\n{i}. URL: {url}")
            print(f"   重复频道 ({len(channels)}个):")
            for j, channel in enumerate(channels, 1):
                print(f"     {j}) {channel}")
    else:
        print("\n✅ 未发现重复的HTTP URL")

if __name__ == "__main__":
    main()
