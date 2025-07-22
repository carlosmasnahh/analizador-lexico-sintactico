section .data
    x dd 0
    y dd 0

section .text
global _start
_start:
    mov dword [x], 3
    mov dword [y], 4
    cmp dword [x], 0
    jne L1
    jmp END_L1
END_L1:
    ; Fin del programa
    mov eax, 1
    int 0x80
