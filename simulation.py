import ins_parser
from sys import stderr, stdout
from ins_parser import insts
import xlwt
from bin_parser import get_hex
from copy import deepcopy
import utils
from utils import printe
from upro import Uinst
from bin_parser import read_bin
import inst
import lst_parser

# TODO: 在这里填入配置信息
"""
ins_path: INS(指令系统)文件路径
bin_path: BIN(EM二进制文件)路径
simulation_times: 模拟的微指令周期数，即模拟多少次"单微指令执行"
"""
ins_path = 'samples/divide/DIVIDE.INS'
bin_path = 'samples/divide/DIVIDE.BIN'
lst_path = 'samples/divide/DIVIDE.LST'
simulation_times = 2000
ins_description = {

}

# simulation

utils.IS_DEBUG_MODE = True

# read macro instructions
um = [
    Uinst(b'\xff\xff\xcb\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
]
ins_parser.init()
addr_to_ins = {}

with open(ins_path, "rb") as f:
    # parse ins
    ins_parser.is_valid_ins_file(f)
    ins_parser.parse_insts(f)
    for ins in ins_parser.insts:
        addr_to_ins[ins.addr] = ins
    addr_to_ins[0] = inst.Inst('_FATCH_', 0)
    # parse uM
    f.read(15)
    for _ in range(252):
        um.append(Uinst(f.read(4)))
print('uM read finished:')
for i in range(256):
    print('uM[{0}]:\t{1}'.format(i, hex(um[i].byte)))

addr_to_ins_text = lst_parser.parse_lst(lst_path)
print('LST read finished.')

# read EM memory
em = read_bin(bin_path)

# virtual devices
pc = 0
upc = 0
A = 0
W = 0
C = 0
Z = 0


class ALU:
    d = 0
    l = 0
    r = 0


alu = ALU()

R = [0] * 4

IR = 0
ST = 0
# IA=E0
MAR = 0

IN = 0
OUT = 0

ABUS = 0
DBUS = 0
IBUS = 0

print('Simulation start:')

uins = lambda: um[upc]


class Log:
    ins: str
    ins_addr: str
    machine_code: str
    ins_description: str
    pc: str
    upc: str
    difference = ""

    def __init__(self):
        self.macro_programs = []


class Status:
    """
    记录运行某时刻的寄存器情况，用于之后进行对比
    """

    def __init__(self):
        self.pc = pc
        self.upc = upc
        self.A = A
        self.W = W
        self.C = C
        self.Z = Z

        self.R = deepcopy(R)

        self.IR = IR
        self.ST = ST

        self.MAR = MAR

        self.IN = IN
        self.OUT = OUT

        self.ABUS = ABUS
        self.DBUS = DBUS
        self.IBUS = IBUS

    def get_difference(self):
        result = []
        if self.pc != pc:
            result.append(('pc', get_hex(pc)))
        if self.upc != upc:
            result.append(('upc', get_hex(upc)))
        if self.A != A:
            result.append(('A', get_hex(A)))
        if self.W != W:
            result.append(('W', get_hex(W)))
        if self.C != C:
            result.append(('C', get_hex(C)))
        if self.Z != Z:
            result.append(('Z', get_hex(Z)))

        for i in range(4):
            if self.R[i] != R[i]:
                result.append(('R[{0}]'.format(i), get_hex(W)))

        if self.MAR != MAR:
            result.append(('MAR', get_hex(MAR)))

        if self.IN != IN:
            result.append(('IN', get_hex(IN)))
        if self.OUT != OUT:
            result.append(('OUT', get_hex(OUT)))

        return result


last_status = Status()


def trace():
    """
    追踪距上一次trace()运行，各主要寄存器的数据变化
    """
    global last_status
    difference = last_status.get_difference()
    last_status = Status()
    return '\n'.join(['{0}: {1}'.format(item[0], item[1]) for item in difference])


def debug_em():
    for i in range(16):
        for j in range(16):
            print(get_hex(em[i * 16 + j]) + ' ', end='')
        print()


run_log = []
# Main Simulation Loop
for time in range(simulation_times):
    print('-------------------------')
    print("circle:{0}\tpc:{1}\tins:{2}".format(time, hex(pc),
                                               addr_to_ins[upc // 4 * 4] if upc // 4 * 4 in addr_to_ins else 'UNDEF'))
    print('upc={0}\t{1}'.format(hex(upc), uins().get_upro()))

    if len(run_log) > 0:
        run_log[-1].macro_programs.append(uins().get_upro())

    """
    处理ABUS地址总线输入
    """
    # address input
    if uins().pcoe():
        ABUS = pc
    if uins().maroe():
        ABUS = MAR

    """
    考虑add等指令，这里认为是先执行运算，再考虑DBUS的输入
    但其实将运算放到微指令周期的最后也可以
    """
    # do ALU calculation
    method = uins().get_ss()
    C_out_D = 0
    if method == 0:
        # add
        alu.d = A + W
        if alu.d >= 256:
            C_out_D = 1
            alu.d -= 256
    elif method == 1:
        # minus
        alu.d = A - W
        if alu.d < 0:
            C_out_D = 1
            alu.d += 256
    elif method == 2:
        # or
        alu.d = A | W
    elif method == 3:
        # and
        alu.d = A & W
    elif method == 4:
        # add with lower
        alu.d = A + W + C
        if alu.d >= 256:
            C_out_D = 1
            alu.d -= 256
    elif method == 5:
        # minus with lower
        alu.d = A - W - C
        if alu.d < 0:
            C_out_D = 1
            alu.d += 256
    elif method == 6:
        # !A
        alu.d = A ^ 255
    elif method == 7:
        # A out
        alu.d = A

    """
    ALU的L/D/R各自维护一个进位标志，实际执行时根据DBUS的连接方式，将对应的Cout/Zout写入C/Z标志位
    CN和FEN同时启用时可能出现问题 建议避免
    """
    alu.l = ((alu.d & 127) << 1) + (C & uins().cn() // 512)
    C_out_L = 1 if alu.d & 128 else 0
    alu.r = ((alu.d & 254) >> 1) + (C & uins().cn() // 512) * 128
    C_out_R = alu.d & 1

    """
    由X2 X1 X0决定DBUS的输入端
    """
    # data -> dbus
    if uins().get_xs() == 0:
        # "用户IN"
        DBUS = 0
    elif uins().get_xs() == 1:
        # "中断地址IA"
        DBUS = 0
    elif uins().get_xs() == 2:
        # "堆栈寄存器ST"
        DBUS = ST
    elif uins().get_xs() == 3:
        # "PC值"
        DBUS = pc
    elif uins().get_xs() == 4:
        # "ALU直通"
        DBUS = alu.d
        if uins().fen():
            C = C_out_D
            Z = (alu.d == 0)
    elif uins().get_xs() == 5:
        # "ALU右移"
        DBUS = alu.r
        if uins().fen():
            C = C_out_R
            Z = (alu.r == 0)
    elif uins().get_xs() == 6:
        # "ALU左移"
        DBUS = alu.l
        if uins().fen():
            C = C_out_L
            Z = (alu.l == 0)
    elif uins().get_xs() == 7:
        # "浮空"
        if uins().emen() and uins().emrd():
            # "EM存储器输入"
            DBUS = em[ABUS]
        elif uins().rrd():
            DBUS = R[IR % 4]
        else:
            DBUS = 0

    """
    依次考虑从DBUS取出数据的操作
    """
    # dbus -> data
    if uins().emen() and uins().emwr():
        em[ABUS] = DBUS
    if uins().maren():
        MAR = DBUS
    if uins().sten():
        st = DBUS
    if uins().rwr():
        R[IR % 4] = DBUS
    if uins().aen():
        A = DBUS
    if uins().wen():
        W = DBUS

    """
    当前微指令执行功能结束，准备下一条指令
    以下三个_next是下一个微指令周期的数据，在本周期完全结束时统一覆盖
    """
    upc_next = upc
    pc_next = pc
    IR_next = IR

    """
    如果iren启用，从内存中读入IR和upc值
    IR值从内存中直接取(包括末两位的R?选择)
    upc需要去除末两位信息，用4对齐地址
    IR的唯一作用是提供R?选择信息，以及决定JMP/JZ/JC的跳转方式
    """
    # uPC
    if uins().iren():
        IR_next = em[pc]
        upc_next = em[pc] // 4 * 4
        printe('got next instruction: {0}\tupc={1}'
               .format(addr_to_ins[upc_next], um[upc_next].get_upro())
               )
        if len(run_log) > 0:
            run_log[-1].difference = trace()
            pass
        run_log.append(Log())
        run_log[-1].ins_addr = get_hex(pc - 1)
        run_log[-1].ins_description = ins_description[upc_next] \
            if upc_next in ins_description else 'Not Defined'
        run_log[-1].machine_code = addr_to_ins[upc_next].get_addr_str()
        run_log[-1].upc = get_hex(upc_next)
        run_log[-1].pc = get_hex(pc)
        run_log[-1].ins = addr_to_ins_text[get_hex(pc)]
    else:
        upc_next = upc + 1

    """
    如果elp打开，赋值pc
    否则pc+1
    注意elp与iren是相互独立的，没有直接关系
    """
    # PC
    if uins().elp():
        if (IR >> 2) % 4 == 0 and C:
            # JC
            pc_next = DBUS
            printe('! jc: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
        elif (IR >> 2) % 4 == 1 and Z:
            # JZ
            pc_next = DBUS
            printe('! jz to: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
        elif (IR >> 2) % 4 == 3:
            pc_next = DBUS
            printe('! jmp to: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
        elif uins().pcoe():
            pc_next = pc + 1
    elif uins().pcoe():
        pc_next = pc + 1

    """
    指令周期最终阶段，覆盖pc/upc/ir，进入下一周期
    """
    pc = pc_next
    upc = upc_next
    IR = IR_next
    pass

print('Simulation completed.')

print('The Final Em is:')
debug_em()

# write runtime logs
print('Output Runtime Logs...')
workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet('ins Trace')
style = xlwt.XFStyle()
font = xlwt.Font()
font.name = "等线"
font.bold = True
font.height = 210
style.font = font
style.alignment.horz = 2
style.alignment.vert = 1
style.alignment.wrap = 1

worksheet.write(0, 0, label="汇编指令", style=style)
worksheet.write(0, 1, label="程序地址", style=style)
worksheet.write(0, 2, label="机器码", style=style)
worksheet.write(0, 3, label="指令说明", style=style)
worksheet.write(0, 4, label="微程序", style=style)
worksheet.write(0, 5, label="PC", style=style)
worksheet.write(0, 6, label="mPC", style=style)
worksheet.write(0, 7, label="运行时寄存器或存储器的值", style=style)
for row, log in enumerate(run_log):
    worksheet.write(row + 1, 0, label=log.ins, style=style)
    worksheet.write(row + 1, 1, label=log.ins_addr, style=style)
    worksheet.write(row + 1, 2, label=log.machine_code, style=style)
    worksheet.write(row + 1, 3, label=log.ins_description, style=style)
    worksheet.write(row + 1, 4, label='\r\n'.join(log.macro_programs), style=style)
    worksheet.write(row + 1, 5, label=log.pc, style=style)
    worksheet.write(row + 1, 6, label=log.upc, style=style)
    worksheet.write(row + 1, 7, label=log.difference, style=style)
workbook.save('Inst Trace.xls')
