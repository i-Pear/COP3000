;程序要求：0FAH内存放起始地址，0FBH内存放乘数字节数，0FCH内存放循环次数（字节*8）
;数据存放：假如乘数为n个字节，起始地址为s，则地址s ~ s+n-1为0，s+n ~ s+2n-1存放第一个乘数，s+2n ~ s+3n-1存放第二个乘数，最后结果存放在s ~ s+2n-1中。
;输出形式：在final程序段轮流输出各地址内的值。R0存放即将输出的地址，R3存放输出值。

MOV A,#0C0H  ;起始地址
MOV 0FAH,A
MOV A,#04H  ;几个字节
MOV 0FBH,A
MOV A,#20H  ;几次循环（字节*8）
MOV 0FCH,A

MOV A,#00H
MOV 0C0H,A
MOV A,#00H
MOV 0C1H,A
MOV A,#00H
MOV 0C2H,A
MOV A,#00H
MOV 0C3H,A
MOV A,#0C3H
MOV 0C4H,A
MOV A,#61H
MOV 0C5H,A
MOV A,#0B6H
MOV 0C6H,A
MOV A,#78H
MOV 0C7H,A
MOV A,#21H
MOV 0C8H,A
MOV A,#0AFH
MOV 0C9H,A
MOV A,#62H
MOV 0CAH,A
MOV A,#0EH
MOV 0CBH,A
;ans:
;19B5 7327 4B39 EA90

LOOP:
    MOV A,0FCH
    MOV R3,A
    ; R1 & 1 ?
    MOV A,0FAH
    ADD A,0FBH
    ADD A,0FBH
    SUB A,#01H ; R1末尾
    MOV R0,A
    MOV A,@R0
    AND A,#01H
    JZ addend
        ; R0 = R0 + R2
        MOV R0,#00H    ; 进位清零
        MOV A,0FBH
        MOV R1,A       ; 几个数
        MOV A,0FAH
        ADD A,0FBH
        MOV R2,A       ; 游标0
        ADD A,0FBH
        ADD A,0FBH
        MOV R3,A       ; 游标1

        addloop:
            MOV A,R1
            ADD A,#00H
            JZ addend
            SUB A,#01H
            MOV R1,A    ; 控制循环次数的计数器

            MOV A,R2
            SUB A,#01H
            MOV R2,A
            MOV A,R3
            SUB A,#01H
            MOV R3,A    ; 修改游标

            MOV A,R0
            ADD A,#0FFH ; 恢复进位位

            MOV A,@R2
            ADDC A,@R3
            MOV @R2,A

            MOV A,#00H
            ADDC A,#00H
            MOV R0,A    ; 保存进位位

        jmp addloop

    addend:

    ; (R0,R1)>>1
    MOV A,0FAH     ; 起始地址
    MOV R0,A
    MOV A,0FBH
    ADD A,0FBH
    MOV R1,A       ; 几个数（字节*2）
    MOV R2,#00H    ; 清空进位位

    rrcloop:
        MOV A,R1
        ADD A,#00H
        JZ loopend
        SUB A,#01H
        MOV R1,A

        MOV A,R2
        ADD A,#0FFH ; 恢复进位位

        MOV A,@R0
        RRC A
        MOV @R0,A

        MOV A,#00H
        ADDC A,#00H
        MOV R2,A    ; 保存进位位

        MOV A,R0
        ADD A,#01H
        MOV R0,A

    JMP rrcloop


loopend:
MOV A,0FCH
SUB A,#01H
MOV 0FCH,A
JZ final
JMP LOOP

final:
MOV A,0FAH
MOV R0,A
ADD A,0FBH
ADD A,0FBH
MOV R1,A
MOV R2,#00H
outputloop:
    MOV A,@R0
    MOV R3,A

    MOV A,R0
    ADD A,#01H
    MOV R0,A
    SUB A,R1
    jz final
    jmp outputloop
