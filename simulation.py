from collections import namedtuple
import ins_parser
from bin_parser import get_hex
from copy import deepcopy
import utils
from upro import Uinst
from bin_parser import read_bin

utils.IS_DEBUG_MODE = True

# filename = input("请输入 *.INS 文件的路径:")
# bin_path = input('请输入 *.BIN 文件的路径:')
filename = 'INST.INS'
bin_path = 'TEST.BIN'

# read macro instructions
um = [
    Uinst(b'\xff\xff\xcb\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
    Uinst(b'\xff\xff\xff\x00'),
]
with open(filename, "rb") as f:
    f.read(15)
    for _ in range(252):
        um.append(Uinst(f.read(4)))

# read instructions
ins_parser.init()
with open(filename, "rb") as f:
    ins_parser.is_valid_ins_file(f)
    ins_parser.parse_insts(f)

# read EM memory
data = read_bin(bin_path)

# simulation
# times = int(input('输入模拟时钟节拍数:'))
times = 20

# virtual devices
pc = 0
upc = 0
A = 0
W = 0
C = 0
Z = 0

alu = namedtuple('ALU_OUT', ['l', 'd', 'r'])(0, 0, 0)

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

# Main Simulation Loop
for time in range(times):
    # address input
    if uins().pcoe():
        ABUS = pc
        pc += 1
    if uins().maroe():
        ABUS = MAR

    # do calculation
    method = uins().get_ss()
    if method == 0:
        # add
        alu.d = A + W
        if alu.d >= 256:
            C = 1
            alu.d -= 256
    elif method == 1:
        # minus
        alu.d =
    elif method == 2:
        # or
        alu.d = A | W
    elif method == 3:
        # and
        alu.d = A & W
    elif method == 4:
        # add with lower
        alu.d =
    elif method == 5:
        # minus with lower
        alu.d =
    elif method == 6:
        # !A
        alu.d =
    elif method == 7:
        # A out
        alu.d = A

    alu.l = (alu.d & 127) << 1
    alu.d = (alu.d & 254) >> 1

    # get symbols
    Z = (alu.d == 0)

    # instruction -> ibus

    # data -> dbus

    # dbus -> data

    # PC / uPC
    if uins().iren():
        upc = IBUS

    pass


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
