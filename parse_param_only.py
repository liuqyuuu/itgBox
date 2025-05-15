import re
from common import *

def extract_parameters(content):
    start = content.find('#(')
    if start == -1:
        return None
    start += 2  # 跳过 '#('
    count = 1
    end = start
    while end < len(content):
        if content[end] == '(':
            count += 1
        elif content[end] == ')':
            count -= 1
            if count == 0:
                break
        end += 1
    if count != 0:
        return None  # 括号不匹配
    return content[start:end]

def remove_comments(text):
    text = re.sub(r'//.*', '', text)  # 去除单行注释
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)  # 去除块注释
    return text

def split_parameters(param_content):
    param_content = remove_comments(param_content)
    params = []
    current = []
    bracket_depth = 0
    for c in param_content:
        if c == '(':
            bracket_depth += 1
            current.append(c)
        elif c == ')':
            bracket_depth -= 1
            current.append(c)
        elif c == ',' and bracket_depth == 0:
            param_str = ''.join(current).strip()
            if param_str:
                params.append(param_str)
            current = []
        else:
            current.append(c)
    # 处理最后一个参数
    param_str = ''.join(current).strip()
    if param_str:
        params.append(param_str)
    return params

def parse_parameter(param_str):

    parts = param_str.split('=')
    
    # 如果没有 '='，返回整个字符串
    if len(parts) != 2:
        print(param_str)
        return
    
    name = parts[0].split('\s')[-1]
    value_str =  parts[1].strip()
    return name, value_str

def main():
    # import sys
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py <verilog_file>")
    #     return
    filename = "test.v"
    with open(filename, 'r') as f:
        content = f.read()
    param_content = extract_parameters(content)
    if not param_content:
        print("No parameters found in #() block.")
        return
    param_list = split_parameters(param_content)
    parameters = []
    for param_str in param_list:
        name, value_str = parse_parameter(param_str)
        if not name or not value_str:
            continue
        param = Param(name=name, value_str = value_str)
        parameters.append(param)
    
    print("\nExtracted parameters:")
    for param in parameters:
        print(f"{param.name}:")
        print(f"  Raw value: {param.value_str}")
        print(f"  Is integer: {param.is_int}")
        print(f"  int_value(): {param.int_value()}\n")

if __name__ == '__main__':
    main()