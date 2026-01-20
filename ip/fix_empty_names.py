#!/usr/bin/env python3
import re

def fix_empty_names():
    fixed_count = 0
    
    with open('./SHIPTV2026.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.startswith('#EXTINF:') and 'tvg-name=""' in line:
            # Extract channel name from end of line (after last comma)
            match = re.search(r',([^,]+)$', line.strip())
            if match:
                channel_name = match.group(1).strip()
                # Replace empty tvg-name with extracted name
                new_line = line.replace('tvg-name=""', f'tvg-name="{channel_name}"')
                lines[i] = new_line
                fixed_count += 1
                print(f"Fixed: {channel_name}")
    
    # Write to new file
    with open('./SHIPTV2026-1.m3u', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n修复完成:")
    print(f"修复空频道名数量: {fixed_count}")
    print("已创建新文件: SHIPTV2026-1.m3u")

if __name__ == "__main__":
    fix_empty_names()
