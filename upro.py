class Uinst:
	"""
	微指令对象
	"""

	def __init__(self, b):
		"""b 为 4 个 bytes"""
		self.byte = (b[2] << 16) + (b[1] << 8) + (b[0])

	def is_default_uint(self):
		"""该微指令是否为默认指令"""
		return self.byte == 0xffffff

	def get_upro(self):
		"""获取微程序"""
		return hex(self.byte)[2:].upper()

	# X2X1X0 对应的数据输出字符串
	xs_map_data_out = [
		"用户IN", "中断地址IA",
		"堆栈寄存器ST", "PC值",
		"ALU直通", "ALU右移",
		"ALU左移", "浮空"
	]

	def get_data_out(self):
		"""获取数据输出"""
		if self.emen():
			return "存贮器值EM"
		if self.rrd():
			return "寄存器值R?"
		return Uinst.xs_map_data_out[self.get_xs()]

	def get_data_in(self):
		"""获取数据打入"""
		b = self.byte
		buf = []
		if self.aen():
			buf.append("寄存器A")
		if self.wen():
			buf.append("寄存器W")
		if self.rwr():
			buf.append("寄存器R?")
		if self.fen():
			buf.append("标志位C，Z")
		if self.emwr():
			buf.append("存贮器EM")
		if self.iren():
			buf.append("指令寄存器IR")
		if self.elp():
			buf.append("寄存器PC")
		if self.maren():
			buf.append("地址寄存器MAR")
		if self.outen():
			buf.append("用户OUT")
		if self.sten():
			buf.append("堆栈寄存器ST")
		return " ".join(buf)

	def get_addr_out(self):
		"""获取地址输出"""
		if self.pcoe():
			return "PC输出"
		if self.maroe():
			return "MAR输出"
		else:
			return "浮空"

	ss_map_calculator = [
		"加运算", "减运算", "或运算", "与运算",
		"带进位加运算", "带进位减运算", "A取反", "A输出"
	]

	def get_calculator(self):
		"""获取运算器"""
		ss = self.get_ss()
		return Uinst.ss_map_calculator[ss]

	def get_bit_shift_control(self):
		"""获取移位控制"""
		xs = self.get_xs()
		cn = self.cn()
		if xs == 5:
			return "右移" if cn else "带进位右移"
		if xs == 6:
			return "左移" if cn else "带进位左移"
		else:
			return ""

	def get_upc(self):
		"""获取 uPC"""
		if self.iren():
			return "写入"
		else:
			return "+1"

	def get_pc(self):
		"""获取 PC"""
		if self.elp():
			return "写入\n"
		if self.pcoe():
			return "+1\n"
		else:
			return "\n"

	def get_xs(self):
		"""计算 X2X1X0 形式的二进制值，对应十进制0-7"""
		x2 = (Uinst.X2_MASK & self.byte) >> 7
		x1 = (Uinst.X1_MASK & self.byte) >> 6
		x0 = (Uinst.X0_MASK & self.byte) >> 5
		return x2 * 4 + x1 * 2 + x0

	def get_ss(self):
		"""计算 S2S1S0 形式的二进制值，对应十进制0-7"""
		s2 = (Uinst.S2_MASK & self.byte) >> 2
		s1 = (Uinst.S1_MASK & self.byte) >> 1
		s0 = (Uinst.S0_MASK & self.byte) >> 0
		return s2 * 4 + s1 * 2 + s0

	def xrd(self):
		return not Uinst.XRD_MASK & self.byte

	def emwr(self):
		return not Uinst.EMWR_MASK & self.byte

	def emrd(self):
		return not Uinst.EMRD_MASK & self.byte

	def pcoe(self):
		return not Uinst.PCOE_MASK & self.byte

	def emen(self):
		return not Uinst.EMEN_MASK & self.byte

	def iren(self):
		return not Uinst.IREN_MASK & self.byte

	def eint(self):
		return not Uinst.EINT_MASK & self.byte

	def elp(self):
		return not Uinst.ELP_MASK & self.byte

	def maren(self):
		return not Uinst.MAREN_MASK & self.byte

	def maroe(self):
		return not Uinst.MAROE_MASK & self.byte

	def outen(self):
		return not Uinst.OUTEN_MASK & self.byte

	def sten(self):
		return not Uinst.STEN_MASK & self.byte

	def rrd(self):
		return not Uinst.RRD_MASK & self.byte

	def rwr(self):
		return not Uinst.RWR_MASK & self.byte

	def cn(self):
		return not Uinst.CN_MASK & self.byte

	def fen(self):
		return not Uinst.FEN_MASK & self.byte

	def x2(self):
		return not Uinst.X2_MASK & self.byte

	def x1(self):
		return not Uinst.X1_MASK & self.byte

	def x0(self):
		return not Uinst.X0_MASK & self.byte

	def wen(self):
		return not Uinst.WEN_MASK & self.byte

	def aen(self):
		return not Uinst.AEN_MASK & self.byte

	def s2(self):
		return not Uinst.S2_MASK & self.byte

	def s1(self):
		return not Uinst.S1_MASK & self.byte

	def s0(self):
		return not Uinst.S0_MASK & self.byte

	# 微指令中 24 个控制位的掩码
	XRD_MASK = 1 << 23
	EMWR_MASK = 1 << 22
	EMRD_MASK = 1 << 21
	PCOE_MASK = 1 << 20
	EMEN_MASK = 1 << 19
	IREN_MASK = 1 << 18
	EINT_MASK = 1 << 17
	ELP_MASK = 1 << 16
	MAREN_MASK = 1 << 15
	MAROE_MASK = 1 << 14
	OUTEN_MASK = 1 << 13
	STEN_MASK = 1 << 12
	RRD_MASK = 1 << 11
	RWR_MASK = 1 << 10
	CN_MASK = 1 << 9
	FEN_MASK = 1 << 8
	X2_MASK = 1 << 7
	X1_MASK = 1 << 6
	X0_MASK = 1 << 5
	WEN_MASK = 1 << 4
	AEN_MASK = 1 << 3
	S2_MASK = 1 << 2
	S1_MASK = 1 << 1
	S0_MASK = 1 << 0
