#!/usr/bin/env python3
import re

def validate_m3u():
    errors = []
    warnings = []
    
    with open('./SHIPTV2026.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check header
    if not lines[0].strip().startswith('#EXTM3U'):
        errors.append("Line 1: Missing #EXTM3U header")
    
    i = 1
    entry_count = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            entry_count += 1
            
            # Check EXTINF format
            if not re.match(r'^#EXTINF:-1\s+', line):
                errors.append(f"Line {i+1}: Invalid EXTINF format: {line[:50]}...")
            
            # Check if next line exists and is URL
            if i + 1 >= len(lines):
                errors.append(f"Line {i+1}: EXTINF without URL")
            else:
                url_line = lines[i + 1].strip()
                if not url_line:
                    errors.append(f"Line {i+2}: Empty URL after EXTINF")
                elif not url_line.startswith('http'):
                    warnings.append(f"Line {i+2}: URL doesn't start with http: {url_line[:50]}...")
            
            # Check tvg-name attribute
            if 'tvg-name=' not in line:
                warnings.append(f"Line {i+1}: Missing tvg-name attribute")
            
            i += 2
        elif line.startswith('#'):
            # Comment or other directive
            i += 1
        elif line.startswith('http'):
            # URL without EXTINF
            warnings.append(f"Line {i+1}: URL without preceding EXTINF: {line[:50]}...")
            i += 1
        elif line == '':
            # Empty line
            i += 1
        else:
            # Unknown content
            warnings.append(f"Line {i+1}: Unknown content: {line[:50]}...")
            i += 1
    
    print("=== M3U文件格式检查结果 ===")
    print(f"总行数: {len(lines)}")
    print(f"频道条目数: {entry_count}")
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors:
            print(f"  {error}")
    else:
        print("\n✅ 未发现格式错误")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for warning in warnings[:10]:  # Show first 10 warnings
            print(f"  {warning}")
        if len(warnings) > 10:
            print(f"  ... 还有 {len(warnings) - 10} 个警告")
    else:
        print("\n✅ 未发现格式警告")
    
    return len(errors) == 0

if __name__ == "__main__":
    is_valid = validate_m3u()
    print(f"\n文件格式: {'有效' if is_valid else '无效'}")
