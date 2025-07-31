#!/usr/bin/env python3
"""
修复 JSONL 文件中的 Unicode 编码问题
将 Unicode 转义序列转换为可读的中文字符
"""

import json
import argparse
import sys

def fix_unicode_file(input_file, output_file=None):
    """修复文件中的 Unicode 编码问题"""
    
    if output_file is None:
        output_file = input_file.replace('.jsonl', '_fixed.jsonl')
    
    print(f"🔧 修复文件: {input_file}")
    print(f"📁 输出到: {output_file}")
    
    try:
        fixed_lines = []
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # 解析 JSON
                    data = json.loads(line)
                    # 重新编码，确保中文字符正常显示
                    fixed_line = json.dumps(data, ensure_ascii=False)
                    fixed_lines.append(fixed_line)
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️  第 {line_num} 行 JSON 解析错误: {e}")
                    print(f"   内容: {line[:100]}...")
                    continue
        
        # 写入修复后的文件
        with open(output_file, 'w', encoding='utf-8') as f:
            for line in fixed_lines:
                f.write(line + '\n')
        
        print(f"✅ 修复完成！")
        print(f"📊 处理了 {len(fixed_lines)} 行数据")
        
        # 显示修复前后对比
        print(f"\n🔍 修复效果对比:")
        if fixed_lines:
            print("修复前:")
            with open(input_file, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                print(f"  {first_line[:80]}...")
            
            print("修复后:")
            print(f"  {fixed_lines[0][:80]}...")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ 文件不存在: {input_file}")
        return False
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='修复 JSONL 文件中的 Unicode 编码问题')
    parser.add_argument('input_file', help='输入的 JSONL 文件路径')
    parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    parser.add_argument('--inplace', action='store_true', help='直接修改原文件')
    
    args = parser.parse_args()
    
    if args.inplace:
        output_file = args.input_file
    else:
        output_file = args.output
    
    success = fix_unicode_file(args.input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()