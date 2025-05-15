from common import *

def isWordChar(c):
    return c.isalnum() or c == "_"

def isLastWordChar(i,s):
    if i == len(s):
        return isWordChar(s[i])
    return isWordChar(s[i]) and not isWordChar(s[i+1]) 

# input code without comment
def arg_default_module(code):
    i = 0
    bracket_stack = []
    status_st = []
    param_list = []
    port_list = []
    data_type = set(["logic","integer","bit","byte","signed","unsigned","enum"])

    cur_word = ""
    cur_value = ""
    cur_width = ""
    for i in range(len(code)):

        # print(status_st)
        # print(bracket_stack)

        char = code[i]

        if not char or char=="\n":
            continue

        if isWordChar(char):
            cur_word += char
            in_word = True  
        elif in_word:
            cur_word = ""
            in_word = False

        if char == "(" or char == "{" or char == "[":
            bracket_stack.append('(')
        if char ==")"or char == "}" or char == "]":
            bracket_stack.pop()

        if cur_word == "module" and isLastWordChar(i,code):
            status_st.append("module")
            print(cur_word)
            continue
        
        if not status_st:
            continue

        if status_st[-1] == "module" and char == "#":
            param_exist = True
            continue

        if status_st[-1] == "module" and len(bracket_stack) == 1:
            if cur_word == "localparam" and isLastWordChar(i,code):
                param_list.append(Param(isLocal=True))
                status_st.append("param")
            if cur_word == "parameter" and isLastWordChar(i,code):
                param_list.append(Param(isLocal=True))
                status_st.append("param")
                continue
        
        if status_st[-1] == "param" and len(bracket_stack) == 1:
            if isLastWordChar(i,code) and cur_word not in data_type:
                param_list[-1].name = cur_word
                continue

        if status_st[-1] == "param" and len(bracket_stack) == 1:
            if char == "=":
                status_st.append("value")
                continue

        if status_st[-1] == "value":
            if (char == "," and len(bracket_stack) == 1) \
                or (char == ")" and len(bracket_stack) == 0):
                status_st.pop() # param after pop
                status_st.pop() # module after pop
                param_list[-1].value_str = cur_value.strip()
                cur_value = ""
                continue
            cur_value += char
        # print(cur_value)

        if status_st[-1] == "module" and len(bracket_stack) ==  1:
            if cur_word == "input" and isLastWordChar(i,code):
                status_st.append("port")
                port_list.append(Port(dir="input"))
                continue
            if cur_word == "output" and isLastWordChar(i,code):
                status_st.append("port")
                port_list.append(Port(dir="output"))
                continue

        if status_st[-1] == "port" and char == "[":
            isMultBits = True
            status_st.append("width")
            # print(bracket_stack)
            continue

        if status_st[-1] == "width":
            if char == "]" and len(bracket_stack) == 1:
                status_st.pop()
                port_list[-1].width_str = cur_width.strip()
                cur_width = ""
                continue
            cur_width += char

        if status_st[-1] == "port" and len(bracket_stack) == 1:
            if isLastWordChar(i,code) and cur_word not in data_type:
                port_list[-1].name = cur_word
                status_st.pop()
                continue

        if status_st[-1] == "module" and not bracket_stack:
            if char == ";":
                print("END of arg param and port")
                break

    print(param_list)
    print(port_list)
    return

if __name__ == '__main__':
    import sys
    # if len(sys.argv) < 2:
    #     print("Usage: python script.py <verilog_file>")
    #     exit()
    # filename = sys.argv[1]
    filename = "test.v"
    code = ""
    with open(filename, 'r') as f:
        code = f.read()
    # print(f"输入: {content}"
    # print(f"输出: {arg_default_module(content)}\n")
    code_wo_comment = remove_comments(code)
    # print(code_wo_comment)
    arg_default_module(code_wo_comment)