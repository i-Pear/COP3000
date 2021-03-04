from upro import Uinst

class Inst:
	"""
	指令对象
	"""

	def __init__(self, op, addr, num1='', num2=''):
		self.__t_cnt = 0
		self.__op = op
		self.addr = addr
		self.__num1 = num1
		self.__num2 = num2
		self.upros = []
		pass

	def get_mnemonic(self):
		"""获取助记符"""
		return self.__str__()

	def get_addr_num(self):
		"""获取地址的数字形式"""
		return self.addr

	def get_addr_str(self):
		"""获取地址的字符串形式"""
		bin_addr = bin(self.addr)[2:].rjust(8, '0')[:-2] + 'xx'
		hex_addr = hex(self.addr)[2:].rjust(2, '0').upper()
		hex_addr_add_3 = hex(self.addr + 3)[2:].rjust(2, '0').upper()
		return f"{bin_addr} {hex_addr}-{hex_addr_add_3}"

	def get_op_num1(self):
		"""获取操作码1"""
		return self.__num1

	def get_op_num2(self):
		"""获取操作码2"""
		return self.__num2

	def get_mache_code1(self):
		"""返回机器码1"""
		return self.get_addr_str()

	def get_mache_code2(self):
		"""返回机器码2"""
		code_need_show_lst = ['#II', 'MM']
		if self.__num1 in code_need_show_lst:
			return self.__num1
		if self.__num2 in code_need_show_lst:
			return self.__num2
		return ""

	def get_mache_code3(self):
		"""返回机器码3"""
		code_need_show_lst = ['#II', 'MM']
		res = []
		if self.__num1 in code_need_show_lst:
			res.append(self.__num1)
		if self.__num2 in code_need_show_lst:
			res.append(self.__num2)
		if len(res) >= 2:
			return res[1]
		return ""

	def get_comment(self):
		"""获取指令注释"""
		if self.__op != "_INT_":
			return "\n"
		else:
			return "实验机占用，不可修改。进入中断时，实验机硬件产生 _INT_ 指令。\n"

	def get_max_t(self):
		return self.__t_cnt

	def add_one_uinst(self, byte):
		"""
			向 self.upros 加入一个 Uinst 对象
			并根据 uinst 的值来判断是否增加 self.__t_cnt
		"""
		uinst = Uinst(byte)
		if not uinst.is_default_uint():
			self.__t_cnt += 1
		self.upros.append(Uinst(byte))

	def __str__(self):
		res=f"{self.__op}"
		if self.__num1!="":
			res=res+f" {self.__num1}"
		if self.__num2!="":
			res=res+f"，{self.__num2}"
		return res
	pass
