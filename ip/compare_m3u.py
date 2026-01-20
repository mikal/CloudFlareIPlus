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

def update_m3u():
    # Parse both files
    channels_2025 = parse_m3u('./SHIPTV2025.m3u')
    channels_2022 = parse_m3u('./SHIPTV2022.m3u')
    
    # Read the 2022 file content
    with open('./SHIPTV2022.m3u', 'r', encoding='utf-8') as f:
        content_2022 = f.readlines()
    
    updated_count = 0
    
    # Find matching channel names with different URLs
    for channel_name in channels_2022:
        if channel_name in channels_2025:
            url_2022 = channels_2022[channel_name]['url']
            url_2025 = channels_2025[channel_name]['url']
            
            if url_2022 != url_2025:
                # Update the URL in 2022 content
                line_num = channels_2022[channel_name]['line_number'] + 1
                if line_num < len(content_2022):
                    content_2022[line_num] = url_2025 + '\n'
                    updated_count += 1
                    print(f"Updated {channel_name}: {url_2022} -> {url_2025}")
    
    # Find new channels in 2025 that don't exist in 2022
    new_channels = []
    with open('./SHIPTV2025.m3u', 'r', encoding='utf-8') as f:
        lines_2025 = f.readlines()
    
    i = 0
    while i < len(lines_2025):
        line = lines_2025[i].strip()
        if line.startswith('#EXTINF:'):
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            if name_match:
                channel_name = name_match.group(1)
                if channel_name not in channels_2022:
                    if i + 1 < len(lines_2025):
                        url = lines_2025[i + 1].strip()
                        if url.startswith('http'):
                            new_channels.append((line, url))
                            print(f"New channel found: {channel_name}")
            i += 2
        else:
            i += 1
    
    # Add separator and new channels if any exist
    if new_channels:
        if not content_2022[-1].endswith('\n'):
            content_2022.append('\n')
        content_2022.append('#' + '='*50 + ' NEW CHANNELS ' + '='*50 + '\n')
        for extinf_line, url in new_channels:
            content_2022.append(extinf_line + '\n')
            content_2022.append(url + '\n')
    
    # Write to new file
    with open('./SHIPTV2026.m3u', 'w', encoding='utf-8') as f:
        f.writelines(content_2022)
    
    print(f"\nTotal channels updated: {updated_count}")
    print(f"Total new channels added: {len(new_channels)}")
    print("Created SHIPTV2026.m3u with updated URLs and new channels")

if __name__ == "__main__":
    update_m3u()
