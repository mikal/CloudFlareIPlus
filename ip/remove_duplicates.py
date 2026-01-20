#!/usr/bin/env python3

def remove_duplicate_urls(input_file, output_file):
    """Remove channels with duplicate HTTP URLs, keep first occurrence"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    seen_urls = set()
    output_lines = []
    i = 0
    
    # Process header
    while i < len(lines) and not lines[i].strip().startswith('#EXTINF:'):
        output_lines.append(lines[i])
        i += 1
    
    # Process channels
    duplicates_removed = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            extinf_line = lines[i]
            if i + 1 < len(lines):
                url_line = lines[i + 1]
                url = url_line.strip()
                
                if url.startswith('http'):
                    if url not in seen_urls:
                        seen_urls.add(url)
                        output_lines.append(extinf_line)
                        output_lines.append(url_line)
                    else:
                        duplicates_removed += 1
                else:
                    output_lines.append(extinf_line)
                    output_lines.append(url_line)
                i += 2
            else:
                output_lines.append(extinf_line)
                i += 1
        else:
            output_lines.append(lines[i])
            i += 1
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    
    return duplicates_removed, len(seen_urls)

def main():
    input_file = '/home/mike/iptv/SHIPTV2026-9-reordered.m3u'
    output_file = '/home/mike/iptv/SHIPTV2026-10.m3u'
    
    duplicates_removed, total_channels = remove_duplicate_urls(input_file, output_file)
    
    print(f"已删除 {duplicates_removed} 个重复URL的频道")
    print(f"保留 {total_channels} 个唯一频道")
    print(f"已保存为: {output_file}")

if __name__ == "__main__":
    main()
