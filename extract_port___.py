import re

class Port:
    def __init__(self, direction, name, width):
        self.direction = direction
        self.name = name
        self.width = width

    def __repr__(self):
        return f"Port(direction={self.direction!r}, name={self.name!r}, width={self.width!r})"

#只存储出现在声明框里的parameter
class Param:
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.isTop = False

    def __repr__(self):
        return f"Param(name={self.name!r}, value={self.value!r})"

# 只存储出现在端口的local，string格式
class localParam:
    def __init__():
        pass

class Module:
    def __init__(self, name):
        self.name = name
        self.port_list = []
        self.param_list = []
        self.local_param_list = []

    def __repr__(self):
        return (f"Module(name={self.name!r},\n"
                f"ports={self.port_list},\n"
                f"params={self.param_list},\n"
                f"local_params={self.local_param_list})")

def remove_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
    return text

def parse_verilog_module(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    content = remove_comments(content)
    content = ' '.join(content.split())
    
    module_match = re.search(
        r'module\s+(\w+)\s*(?:#\s*\((.*?)\)\s*)?\((.*?)\)\s*;',
        content
    )
    if not module_match:
        raise ValueError("No module declaration found")
    
    module_name = module_match.group(1)
    params_str = module_match.group(2) or ''
    ports_str = module_match.group(3) or ''
    
    module_body_start = module_match.end()
    module_body = content[module_body_start:]
    endmodule_pos = module_body.find('endmodule')
    if endmodule_pos != -1:
        module_body = module_body[:endmodule_pos]
    
    module = Module(module_name)
    
    # Step1 Parse module parameters
    module_params = []
    for match in re.finditer(r'(?:parameter\s+)?(\w+)\s*=\s*(\d+)', params_str):
        module_params.append(Param(match.group(1), int(match.group(2))))
    module.param_list.extend(module_params)
    
    # Step2 Parse ports
    # width以字符串形式存储，eval尝试计算，不能计算则添加到localparam
    port_groups = re.finditer(r'(input|output|inout)\s*(?:\[([^\]]*)\])?\s*((?:\w+\s*,?\s*)+)', ports_str)
    for match in port_groups:
        direction, width, names_str = match.groups()
        names = [n.strip() for n in names_str.split(',') if n.strip()]
        for name in names:
            module.port_list.append(Port(direction, name, width))
    
    # Step3 查找需要的localparam。以字符串形式存储localparam表达式

    # Parse body parameters
    param_re = re.compile(r'\b(parameter|localparam)\b\s+(?:.*?\s+)?(\w+)\s*=\s*(\d+)')
    for match in param_re.finditer(module_body):
        p_type, name, value = match.groups()
        param = Param(name, int(value))
        if p_type == 'parameter':
            module.param_list.append(param)
        else:
            module.local_param_list.append(param)
    
    return module

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python verilog_parser.py <verilog_file>")
        sys.exit(1)
    
    try:
        module = parse_verilog_module(sys.argv[1])
        for item in module.param_list:
            print(item)
        for item in module.local_param_list:
            print(item)
        # for item in module.port_list:
        #     print(item)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)