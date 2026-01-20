#!/usr/bin/env python3
import re
from collections import defaultdict

def organize_by_group():
    groups = defaultdict(list)
    header = ""
    
    with open('./SHIPTV2026-6-1.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Save header
    if lines[0].startswith('#EXTM3U'):
        header = lines[0]
    
    # Parse channels by group
    i = 1 if header else 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # Extract group-title
            group_match = re.search(r'group-title="([^"]*)"', line)
            group_name = group_match.group(1) if group_match else "未分组"
            
            # Get URL line
            url_line = lines[i + 1] if i + 1 < len(lines) else ""
            
            # Add to group
            groups[group_name].append((line, url_line))
            i += 2
        else:
            i += 1
    
    # Write organized file
    with open('./SHIPTV2026-7.m3u', 'w', encoding='utf-8') as f:
        # Write header
        if header:
            f.write(header)
        
        # Write groups
        for group_name in sorted(groups.keys()):
            channels = groups[group_name]
            
            # Write group comment
            f.write(f'\n# ========== {group_name} ({len(channels)}个频道) ==========\n')
            
            # Write channels in this group
            for extinf_line, url_line in channels:
                f.write(extinf_line + '\n')
                f.write(url_line)
    
    print(f"文件整理完成:")
    print(f"总分组数: {len(groups)}")
    for group_name in sorted(groups.keys()):
        print(f"  {group_name}: {len(groups[group_name])}个频道")
    print("已创建新文件: SHIPTV2026-7.m3u")

if __name__ == "__main__":
    organize_by_group()
