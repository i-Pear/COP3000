def parse_lst(filename):
    """
    从LST文件获取 指令地址->指令原文 的映射
    :param filename: LST file path
    :return: dict
    """
    addr_to_ins_text = {}
    with open(filename) as f:
        for line in f:
            if len(line) > 0 and line[0] != ' ':
                addr_to_ins_text[line.split()[0]] = line[12:].split(';')[0].strip()
    return addr_to_ins_text
