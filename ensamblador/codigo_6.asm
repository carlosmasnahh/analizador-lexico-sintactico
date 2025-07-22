section .data
    1 dd 0
    t1 dd 0
    t2 dd 0
    t3 dd 0
    t4 dd 0
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
    mov eax, [y]
    sub eax, [1]
    mov [t2], eax
    mov eax, [x]
    mov [t3], eax
    mov eax, [x]
    mov [t4], eax
