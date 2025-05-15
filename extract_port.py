import re
from collections import defaultdict

class Port:
    def __init__(self, direction, name, width_str, unpacked_str, packed_dims, unpacked_dims):
        self.direction = direction
        self.name = name
        self.width_str = re.sub(r'\s+', '', width_str)  # 打包维度
        self.unpacked_str = re.sub(r'\s+', '', unpacked_str)  # 非打包维度
        self.packed_dims = packed_dims
        self.unpacked_dims = unpacked_dims
        self.isPack = (unpacked_dims == 0) and (packed_dims >= 1)
        self.Depth = packed_dims + unpacked_dims
        self.unresolved_vars = set()

    def parse_width_vars(self):
        """解析所有维度表达式中的标识符"""
        # 解析打包维度
        if self.width_str:
            self._parse_single_expr(self.width_str)
        # 解析非打包维度
        if self.unpacked_str:
            self._parse_single_expr(self.unpacked_str)

    def _parse_single_expr(self, expr):
        """提取表达式中的所有标识符"""
        identifiers = re.findall(
            r'(?<!\$)\b([a-zA-Z_]\w*)\b(?=\s*[\?:]|[\s\]\W])',  # 排除系统标识符
            expr
        )
        for var in set(identifiers):
            if not var.isdigit():
                self.unresolved_vars.add(var)

class VerilogParser:
    def __init__(self):
        self.ports = []
        self.local_param_to_find = set()
    
    def extract_module_ports(self, content):
        """提取模块端口声明部分"""
        module_pattern = r'module\s+\w+\s*#?\(.*?\)?\s*\((.*?)\)\s*;'
        match = re.search(module_pattern, content, re.DOTALL)
        return match.group(1) if match else ""

    def parse_port_declaration(self, decl):
        """解析单个端口声明"""
        port_re = re.compile(
            r'^\s*(input|output|inout)\s*'    # 方向
            r'((?:\[.*?\])*)'                 # 打包维度
            r'\s*(?:reg|wire)?\s*'            # 类型修饰
            r'(\w+)'                          # 端口名称
            r'\s*((?:\[.*?\])*)'              # 非打包维度
            r'\s*(?:=.*?)?$',                 # 忽略默认值
            re.IGNORECASE
        )
        
        if match := port_re.match(decl.strip()):
            direction = match.group(1).lower()
            packed_str = match.group(2).strip()
            name = match.group(3)
            unpacked_str = match.group(4).strip()

            packed_dims = len(packed_str[1:-1].split('][')) if packed_str else 0
            unpacked_dims = len(unpacked_str[1:-1].split('][')) if unpacked_str else 0

            return Port(direction, name, packed_str, unpacked_str, packed_dims, unpacked_dims)
        return None

    def analyze_ports(self, content):
        """主分析逻辑"""
        port_content = self.extract_module_ports(content)
        print(port_content)
        port_content = re.sub(r'//.*?(\n|$)|\/\*[\s\S]*?\*\/', '', port_content)
        print(port_content)
        port_decls = [p.strip() for p in re.split(r',(?![^\[]*\])', port_content) if p.strip()]
        
        for decl in port_decls:
            if port := self.parse_port_declaration(decl):
                port.parse_width_vars()  # 不再传入已知参数
                self.ports.append(port)
                self.local_param_to_find.update(port.unresolved_vars)

    def print_report(self):
        """输出分析报告"""
        print("\nPort Analysis Report:")
        header = "{:<8} {:<15} {:<25} {:<8} {:<6} {:<20}"
        print(header.format(
            "Dir", "Name", "Width", "isPack", "Depth", "Unresolved Vars"))
        print("-"*80)
        
        for port in self.ports:
            width = f"{port.width_str}{f' {port.unpacked_str}' if port.unpacked_str else ''}"
            print(header.format(
                port.direction.upper(),
                port.name,
                width,
                str(port.isPack),
                port.Depth,
                ", ".join(port.unresolved_vars) or "None"
            ))
        print("\nParameters to find:", self.local_param_to_find or "None")

# 测试用例
if __name__ == "__main__":
    vlog_code = """
module top #(
    parameter WIDTH = 8,
    parameter SEL = 1
) (
    input [WIDTH-1:0][SEL+1:0]  data_in,  // 应捕获WIDTH和SEL
    output [31:0]               data_out [SIZE-1:0],
    // test
    input [SEL ? 8 : WIDTH]     config,
    /*

    input test,
    */
    inout [3:0]                 io_bus [DEPTH-1:0]
);
endmodule
"""
    
    parser = VerilogParser()
    parser.analyze_ports(vlog_code)
    parser.print_report()