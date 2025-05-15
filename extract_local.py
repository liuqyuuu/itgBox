import re
import sys
from collections import namedtuple

Param = namedtuple('Param', ['name', 'value', 'isLocal', 'isPortNeed'])

def clean_value(value):
    """清理参数值中的多余空格和换行"""
    return re.sub(r'\s+', ' ', value).strip()

def extract_params(content, params_to_find):
    param_list = []
    found = set()
    
    # 匹配parameter/localparam声明（支持多行和复杂表达式）
    pattern = r'''
        (localparam|parameter)\b
        (?:[\s\S]*?\b(?:integer|real|time|realtime)\b)?  # 可选类型修饰
        (?:[\s\S]*?=\s*)?  # 可选赋值符号
        (?:\#\(.*?\))?      # 忽略可能的延迟值
        ([\w]+)             # 参数名
        \s*
        (?:=|;)             # 赋值或声明结束
        ([\s\S]*?)          # 参数值（可能跨多行）
        (?=;\s*(?:localparam|parameter|\}|module|\)|input|output))
    '''
    
    for match in re.finditer(pattern, content, re.VERBOSE):
        param_type, name, raw_value = match.groups()
        print(param_type)
        if name not in params_to_find:
            continue
            
        # 提取到有效值后停止（直到分号或下一个参数声明）
        value = re.split(r'[\s;]', raw_value, 1)[0]
        value = clean_value(value)
        
        param_list.append(Param(
            name=name,
            value=value,
            isLocal=param_type.lower() == 'localparam',
            isPortNeed=param_type.lower() == 'parameter'
        ))
        found.add(name)
    
    return param_list, sorted(params_to_find - found)

def parse_verilog(file_path, params_to_find):
    with open(file_path, 'r') as f:
        content = f.read()
    # print(f"Before: {content}")
    # 移除注释（保护字符串内容）
    content = re.sub(r'//.*?$|/\*[\s\S]*?\*/', '', content, flags=re.MULTILINE)
    # 移除换行和多余空格
    content = re.sub(r'\s+', ' ', content)
    print(f"After remove comment: {content}")
    return extract_params(content, set(params_to_find))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python param_finder.py <verilog_file> <param1> [param2 ...]")
        sys.exit(1)
    
    verilog_file = sys.argv[1]
    target_params = sys.argv[2:]
    print(f"Target Param: {target_params}")
    params, missing = parse_verilog(verilog_file, target_params)
    
    print("\n=== Parameter Report ===")
    for p in params:
        print(f"Name: {p.name}")
        print(f"Value: {p.value}")
        print(f"Local: {p.isLocal}\tPortNeed: {p.isPortNeed}")
        print("-" * 50)
    
    if missing:
        print("\n!!! Missing parameters:", ", ".join(missing))
