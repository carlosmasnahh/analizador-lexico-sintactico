section .data
    t1 dd 0
    x dd 0
    y dd 0

section .text
global _start
_start:
    mov dword [x], 3
    mov dword [y], 4
    mov eax, [x]
    add eax, [y]
    mov [t1], eax
    ; Fin del programa
    mov eax, 1
    int 0x80
