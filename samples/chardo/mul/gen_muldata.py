# 本文件用于生成多位乘法(infmul)所需的准备数据。生成后请替换ASM文件的头部。

# start = input('start pos:')
# first = input('first num:')
# second = input('second num:')
start = 'C0'
first = 'C361B678'
second = '21AF620E'
# ans: 19B5 7327 4B39 EA90

start = int(start,16)
ans = str(hex(int(first,16)*int(second,16)))[2:].upper()
if len(ans)%2==1:
    ans='0'+ans
ans = [ans[i:i+2] for i in range(0,len(ans),2)]
print(f'{first} * {second} = {" ".join(ans)}\n\n')

first = [first[i:i+2] for i in range(0,len(first),2)]
second = [second[i:i+2] for i in range(0,len(second),2)]
assert(len(first)==len(second))

nbytes = len(first)

def writeMM(data,pos):
    if isinstance(data, int):
        data = str(hex(data))[2:]
    pos = pos[2:]
    if data[0].isalpha() or len(data)<2:
        data = '0' + data
    if pos[0].isalpha() or len(pos)<2:
        pos = '0' + pos
    # print(f'MOV  {pos.upper()}H,#{data.upper()}H')
    print(f'MOV  A,#{data.upper()}H\nMOV  {pos.upper()}H,A')

writeMM(start,'0xFA')       #起始地址
writeMM(nbytes,'0xFB')      #几个字节
writeMM(nbytes*8,'0xFC')    #几次循环（字节*8）
print()

for i in range(nbytes):
    writeMM(0,hex(start+i))
for i in range(nbytes):
    writeMM(first[i],hex(start+nbytes+i))
for i in range(nbytes):
    writeMM(second[i],hex(start+nbytes*2+i))

