from sys import stderr, exit

"""
辅助工具
"""

IS_DEBUG_MODE = True


def error(msg):
	"""输出错误信息并退出"""
	print(f"[ERROR] {msg}", file=stderr)
	exit(-1)


def log(msg):
	"""仅在 DEBUG 模式下输出信息"""
	if IS_DEBUG_MODE:
		print(f"[DEBUG] {msg}", file=stderr)


def read(f, size=1):
	"""
		读文件，在遇到 EOF 时抛出 EOFError
		判断的依据用 b''
	"""
	data = f.read(size)
	if data == b'':
		raise EOFError
	else:
		return data


def handle_00_byte(f):
	"""跳过文件中的 \x00"""
	ret = read(f)
	while ret == b'\x00':
		log("跳过一个 \\x00")
		ret = read(f)
	return ret
