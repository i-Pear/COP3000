import struct

dic = "0123456789ABCDEF"


def get_hex(n):
    result = '0' if n < 16 else dic[n // 16]
    return result + dic[n % 16]


def read_bin(filename):
    with open(filename, 'rb') as binFile:
        context = binFile.read(256)
        data = [ord(i) for i in struct.unpack('256c', context)]
        print('EM memory is:')
        for i in range(16):
            for j in range(16):
                print(get_hex(data[i * 16 + j])+' ', end='')
            print()
        return data


if __name__ == '__main__':
    read_bin('TEST.BIN')
