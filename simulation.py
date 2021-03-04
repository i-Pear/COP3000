import ins_parser
from sys import stderr, stdout
from ins_parser import insts
from bin_parser import get_hex
from copy import deepcopy
import utils
from utils import printe
from upro import Uinst
from bin_parser import read_bin
import inst

utils.IS_DEBUG_MODE = True

# filename = input("请输入 *.INS 文件的路径:")
# bin_path = input('请输入 *.BIN 文件的路径:')
filename = 'MUL.INS'
bin_path = 'MUL.BIN'

# read macro instructions
um = [
    Uinst(b'\xff\xff\xcb\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
]
ins_parser.init()
addr_to_ins = {}

with open(filename, "rb") as f:
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

# read EM memory
em = read_bin(bin_path)

# simulation
# times = int(input('输入模拟时钟节拍数:'))
times = 2000

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


def debug_em():
    for i in range(16):
        for j in range(16):
            print(get_hex(em[i * 16 + j]) + ' ', end='')
        print()


# Main Simulation Loop
for time in range(times):
    print('-------------------------')
    print("circle:{0}\tpc:{1}\tins:{2}".format(time, hex(pc),
                                               addr_to_ins[upc // 4 * 4] if upc // 4 * 4 in addr_to_ins else 'UNDEF'))
    print('upc={0}\t{1}'.format(hex(upc), uins().get_upro()))
    # address input
    if uins().pcoe():
        ABUS = pc
    if uins().maroe():
        ABUS = MAR

    # do calculation
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

    alu.l = ((alu.d & 127) << 1) + (C & uins().cn() // 512)
    C_out_L = 1 if alu.d & 128 else 0
    alu.r = ((alu.d & 254) >> 1) + (C & uins().cn() // 512) * 128
    C_out_R = alu.d & 1

    # get symbols
    # CN和FEN同时启用时可能出现问题 建议避免

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
        # "ALU直通
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

    upc_next = upc
    pc_next = pc
    IR_next = IR

    # uPC
    if uins().iren():
        IR_next = em[pc]
        upc_next = em[pc] // 4 * 4
        printe('got next instruction: {0}\tupc={1}'
               .format(addr_to_ins[upc_next // 4 * 4], um[upc_next].get_upro())
               )
    else:
        upc_next = upc + 1

    # PC
    if uins().elp():
        if (IR >> 2) % 4 == 0 and C:
            # JC
            pc_next = DBUS
            printe('! jc: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
            stderr.flush()
        elif (IR >> 2) % 4 == 1 and Z:
            # JZ
            pc_next = DBUS
            printe('! jz to: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
            stderr.flush()
        elif (IR >> 2) % 4 == 3:
            pc_next = DBUS
            printe('! jmp to: pc set to:{1}\tnext_ins={0}'
                   .format(addr_to_ins[em[pc_next] // 4 * 4], hex(pc_next))
                   )
            stderr.flush()
        elif uins().pcoe():
            pc_next = pc + 1
    elif uins().pcoe():
        pc_next = pc + 1

    pc = pc_next
    upc = upc_next
    IR = IR_next
    pass

print('Simulation completed.')
print('The Final Em is:')
debug_em()


class Status:
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
    global last_status
    difference = last_status.get_difference()
    last_status = Status()
    return difference
