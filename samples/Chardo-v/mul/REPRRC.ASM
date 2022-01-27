MOV  R0,#80H  ;起始地址80H
MOV  R1,#04H  ;几个数
MOV  R2,#00H  ;进位位

MOV  A,#54H
MOV  80H,A
MOV  A,#55H
MOV  81H,A
MOV  A,#32H
MOV  82H,A
MOV  A,#33H
MOV  83H,A
; 0x54553233H >> 1 = 
; 0x2A2A9919H

mov R2,#00H ;清空进位位

loop:
    mov A,R1
    add A,#00H
    jz end0
    sub A,#01H
    mov R1,A

    mov A,R2
    add A,#0FFH ;恢复进位位

    mov A,@R0
    RRC A
    mov @R0,A

    mov A,#00H
    addc A,#00H
    mov R2,A ;保存进位位

    mov A,R0
    add A,#01H
    mov R0,A

jmp loop


end0:
mov A,80H
mov R0,A
mov A,81H
mov R1,A
mov A,82H
mov R2,A
mov A,83H
mov R3,A
jmp end0
