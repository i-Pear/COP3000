from sys import argv
import ins_parser
import utils

utils.IS_DEBUG_MODE = True

try:
	filename = argv[1]
except IndexError:
	filename = input("请输入 *.INS 文件的路径:")

ins_parser.init()
with open(filename, "rb") as f:
	ins_parser.is_valid_ins_file(f)
	ins_parser.parse_insts(f)
	ins_parser.generate_insts_csv_file(f)
	ins_parser.parse_upros(f)
	ins_parser.generate_upros_csv_file(f)
