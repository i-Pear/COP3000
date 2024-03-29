import struct
import csv
header = [0x49,0x4e,0x53,0x54,0x55,0x52,0x43,0x54,0x49,0x4f,0x4e,0x20,0x26,0x20,0x75,0x4d,0x20,0x66,0x69,0x6c,0x65,0x20,0x66,0x6f,0x72,0x20,0x43,0x4f,0x50,0x32,0x30,0x30,0x30,0x1a,0x01,0x07,0x5f,0x46,0x41,0x54,0x43,0x48,0x5f,0x00,0x00,0x00,0x46,0xca,0xb5,0xd1,0xe9,0xbb,0xfa,0xd5,0xbc,0xd3,0xc3,0xa3,0xac,0xb2,0xbb,0xbf,0xc9,0xd0,0xde,0xb8,0xc4,0xa1,0xa3,0xb8,0xb4,0xce,0xbb,0xba,0xf3,0xa3,0xac,0xcb,0xf9,0xd3,0xd0,0xbc,0xc4,0xb4,0xe6,0xc6,0xf7,0xc7,0xe5,0x30,0xa3,0xac,0xca,0xd7,0xcf,0xc8,0xd6,0xb4,0xd0,0xd0,0x20,0x5f,0x46,0x41,0x54,0x43,0x48,0x5f,0x20,0xd6,0xb8,0xc1,0xee,0xc8,0xa1,0xd6,0xb8]
intcode = [0x3b,0xca,0xb5,0xd1,0xe9,0xbb,0xfa,0xd5,0xbc,0xd3,0xc3,0xa3,0xac,0xb2,0xbb,0xbf,0xc9,0xd0,0xde,0xb8,0xc4,0xa1,0xa3,0xbd,0xf8,0xc8,0xeb,0xd6,0xd0,0xb6,0xcf,0xca,0xb1,0xa3,0xac,0xca,0xb5,0xd1,0xe9,0xbb,0xfa,0xd3,0xb2,0xbc,0xfe,0xb2,0xfa,0xc9,0xfa,0x20,0x5f,0x49,0x4e,0x54,0x5f,0x20,0xd6,0xb8,0xc1,0xee]
emptycode = [0xff,0xff,0xcb,0xff,0xff,0xff,0xff,0x00,0xff,0xff,0xff,0x00,0xff,0xff,0xff,0x00]
op_num_map = {'':0x00, 'A':0x01, 'R?':0x02, '@R?':0x03, '#II':0x04, 'MM':0x05}
instructions = []
addr = 0
with open('ins_table.csv', 'r', newline='') as csvfile:
    spamreader = csv.reader(csvfile)
    next(spamreader)
    for row in spamreader:
        tmpins = [row[1].split(' ')[0]]
        if len(row[1].split(' '))>1:
            tmpins += row[1].split(' ')[1].split(',')
        while len(tmpins) < 3:
            tmpins += ['']
        row[2] = [i[4:6]+i[2:4]+i[0:2]+i[6:] if i else i for i in row[2].split(' ') ]
        row[2] = ''.join(row[2])
        tmpins.append([row[2][i:i+2] for i in range(0,len(row[2]),2)])
        instructions.append(tmpins)


with open("INST.INS","wb") as f:
    for i in header:
        f.write(struct.pack('B',i))

    for ins in instructions[1:]:
        addr += 4
        if ins[0] == '':
            f.write(struct.pack('B',0x00))
            continue
        f.write(struct.pack('B',0x01))
        f.write(struct.pack('B',len(ins[0])))
        f.write(ins[0].encode())
        f.write(struct.pack('B',addr))
        f.write(struct.pack('B',op_num_map[ins[1]]))
        f.write(struct.pack('B',op_num_map[ins[2]]))
        if ins[0] != '_INT_':
            f.write(struct.pack('B',0x00))
        else:
            for i in intcode:
                f.write(struct.pack('B',i))
    for ins in instructions:
        print(ins)
        if ins[3]:
            for i in ins[3]:
                f.write(struct.pack('B',int(i,16)))
        else:
            for i in emptycode:
                f.write(struct.pack('B',i)) 
