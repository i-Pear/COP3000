;����Ҫ��0FAH�ڴ����ʼ��ַ��0FBH�ڴ�ų����ֽ�����0FCH�ڴ��ѭ���������ֽ�*8��
;���ݴ�ţ��������Ϊn���ֽڣ���ʼ��ַΪs�����ַs ~ s+n-1Ϊ0��s+n ~ s+2n-1��ŵ�һ��������s+2n ~ s+3n-1��ŵڶ�������������������s ~ s+2n-1�С�
;�����ʽ����final����������������ַ�ڵ�ֵ��R0��ż�������ĵ�ַ��R3������ֵ��

MOV A,#0C0H  ;��ʼ��ַ
MOV 0FAH,A
MOV A,#04H  ;�����ֽ�
MOV 0FBH,A
MOV A,#20H  ;����ѭ�����ֽ�*8��
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
    SUB A,#01H ; R1ĩβ
    MOV R0,A
    MOV A,@R0
    AND A,#01H
    JZ addend
        ; R0 = R0 + R2
        MOV R0,#00H    ; ��λ����
        MOV A,0FBH
        MOV R1,A       ; ������
        MOV A,0FAH
        ADD A,0FBH
        MOV R2,A       ; �α�0
        ADD A,0FBH
        ADD A,0FBH
        MOV R3,A       ; �α�1

        addloop:
            MOV A,R1
            ADD A,#00H
            JZ addend
            SUB A,#01H
            MOV R1,A    ; ����ѭ�������ļ�����

            MOV A,R2
            SUB A,#01H
            MOV R2,A
            MOV A,R3
            SUB A,#01H
            MOV R3,A    ; �޸��α�

            MOV A,R0
            ADD A,#0FFH ; �ָ���λλ

            MOV A,@R2
            ADDC A,@R3
            MOV @R2,A

            MOV A,#00H
            ADDC A,#00H
            MOV R0,A    ; �����λλ

        jmp addloop

    addend:

    ; (R0,R1)>>1
    MOV A,0FAH     ; ��ʼ��ַ
    MOV R0,A
    MOV A,0FBH
    ADD A,0FBH
    MOV R1,A       ; ���������ֽ�*2��
    MOV R2,#00H    ; ��ս�λλ

    rrcloop:
        MOV A,R1
        ADD A,#00H
        JZ loopend
        SUB A,#01H
        MOV R1,A

        MOV A,R2
        ADD A,#0FFH ; �ָ���λλ

        MOV A,@R0
        RRC A
        MOV @R0,A

        MOV A,#00H
        ADDC A,#00H
        MOV R2,A    ; �����λλ

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