MOV  R0,#80H  ;��ʼ��ַ80H
MOV  R1,#04H  ;������
MOV  R2,#00H  ;��λλ

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

mov R2,#00H ;��ս�λλ

loop:
    mov A,R1
    add A,#00H
    jz end0
    sub A,#01H
    mov R1,A

    mov A,R2
    add A,#0FFH ;�ָ���λλ

    mov A,@R0
    RRC A
    mov @R0,A

    mov A,#00H
    addc A,#00H
    mov R2,A ;�����λλ

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