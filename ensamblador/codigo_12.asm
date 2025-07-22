section .data
    x dd 0

section .text
global _start
_start:
    mov dword [x], 5
    ; Fin del programa
    mov eax, 1
    int 0x80
