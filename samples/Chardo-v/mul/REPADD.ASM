MOV  R0,#80H  ;��ʼ��ַ80H/��λ
MOV  R1,#04H  ;������
MOV  R2,#00H  ;�α�0
MOV  R3,#00H  ;�α�1

MOV  A,#54H
MOV  80H,A
MOV  A,#55H
MOV  81H,A
MOV  A,#32H
MOV  82H,A
MOV  A,#33H
MOV  83H,A

MOV  A,#70H
MOV  84H,A
MOV  A,#68H
MOV  85H,A
MOV  A,#58H
MOV  86H,A
MOV  A,#0FFH
MOV  87H,A
; ans: C4BD 8B32

mov A,R0
add A,R1
mov R2,A
add A,R1
mov R3,A

mov R0,#00H

loop:
    mov A,R1
    add A,#00H
    jz end0
    sub A,#01H
    mov R1,A ; ����ѭ�������ļ�����

    mov A,R2
    sub A,#01H
    mov R2,A
    mov A,R3
    sub A,#01H
    mov R3,A  ; �޸��α�

    mov A,R0
    add A,#0FFH ;�ָ���λλ

    mov A,@R2
    addc A,@R3
    mov @R2,A

    mov A,#00H
    addc A,#00H
    mov R0,A  ;�����λλ

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