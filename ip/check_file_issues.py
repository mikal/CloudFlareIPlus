#!/usr/bin/env python3

def check_m3u_file(file_path):
    """Comprehensive check of M3U file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    issues = []
    stats = {
        'total_lines': len(lines),
        'channels': 0,
        'extinf_lines': 0,
        'url_lines': 0,
        'http_urls': 0,
        'empty_lines': 0,
        'comment_lines': 0
    }
    
    # Check header
    if not lines[0].strip().startswith('#EXTM3U'):
        issues.append("文件不以 #EXTM3U 开头")
    
    # Analyze each line
    orphaned_extinf = []
    orphaned_urls = []
    duplicate_urls = {}
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            stats['empty_lines'] += 1
        elif line.startswith('#EXTINF:'):
            stats['extinf_lines'] += 1
            # Check if next line is URL
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line.startswith('http'):
                    stats['channels'] += 1
                    stats['http_urls'] += 1
                    # Check for duplicates
                    if next_line in duplicate_urls:
                        duplicate_urls[next_line] += 1
                    else:
                        duplicate_urls[next_line] = 1
                    i += 2
                    continue
                else:
                    orphaned_extinf.append(i + 1)
            else:
                orphaned_extinf.append(i + 1)
        elif line.startswith('http'):
            stats['url_lines'] += 1
            orphaned_urls.append(i + 1)
        elif line.startswith('#'):
            stats['comment_lines'] += 1
        
        i += 1
    
    # Find actual duplicates
    duplicates = {url: count for url, count in duplicate_urls.items() if count > 1}
    
    # Report issues
    if orphaned_extinf:
        issues.append(f"发现 {len(orphaned_extinf)} 个孤立的 #EXTINF 行 (缺少URL): {orphaned_extinf[:5]}")
    
    if orphaned_urls:
        issues.append(f"发现 {len(orphaned_urls)} 个孤立的 URL 行 (缺少#EXTINF): {orphaned_urls[:5]}")
    
    if duplicates:
        issues.append(f"发现 {len(duplicates)} 个重复的URL")
    
    return stats, issues, duplicates

def main():
    file_path = '/home/mike/iptv/SHIPTV2026-11.m3u'
    
    print(f"检查文件: {file_path}")
    
    stats, issues, duplicates = check_m3u_file(file_path)
    
    print(f"\n📊 文件统计:")
    print(f"  总行数: {stats['total_lines']}")
    print(f"  频道数: {stats['channels']}")
    print(f"  #EXTINF行: {stats['extinf_lines']}")
    print(f"  HTTP URL行: {stats['http_urls']}")
    print(f"  注释行: {stats['comment_lines']}")
    print(f"  空行: {stats['empty_lines']}")
    
    if issues:
        print(f"\n⚠️  发现 {len(issues)} 个问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\n✅ 文件格式正常，无问题发现")
    
    if duplicates:
        print(f"\n🔄 重复URL详情:")
        for url, count in list(duplicates.items())[:5]:
            print(f"  {url} (出现{count}次)")
        if len(duplicates) > 5:
            print(f"  ... 还有 {len(duplicates) - 5} 个重复URL")

if __name__ == "__main__":
    main()
