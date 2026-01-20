#!/usr/bin/env python3

def remove_url_duplicates():
    seen_urls = set()
    cleaned_lines = []
    removed_count = 0
    
    with open('./SHIPTV2026-2.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                
                if url.startswith('http'):
                    if url not in seen_urls:
                        seen_urls.add(url)
                        cleaned_lines.append(lines[i])  # EXTINF line
                        cleaned_lines.append(lines[i + 1])  # URL line
                    else:
                        removed_count += 1
                        # Extract channel name for logging
                        import re
                        name_match = re.search(r'tvg-name="([^"]*)"', line)
                        channel_name = name_match.group(1) if name_match else "Unknown"
                        print(f"Removed duplicate URL: {channel_name} - {url}")
                else:
                    # Keep non-http lines
                    cleaned_lines.append(lines[i])
                    cleaned_lines.append(lines[i + 1])
            else:
                cleaned_lines.append(lines[i])
            i += 2
        else:
            # Keep header and other lines
            cleaned_lines.append(lines[i])
            i += 1
    
    # Write to new file
    with open('./SHIPTV2026-3.m3u', 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"\n清理完成:")
    print(f"移除重复URL条目: {removed_count}")
    print(f"保留唯一URL数量: {len(seen_urls)}")
    print("已创建新文件: SHIPTV2026-3.m3u")

if __name__ == "__main__":
    remove_url_duplicates()
