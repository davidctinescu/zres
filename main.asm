extern WriteConsoleA
extern GetStdHandle
extern ExitProcess
    
global main

section .data
stdout dd 0
msg_2 db 'hello', 0xA, 0
len equ $ - msg_2

section .bss
written resd 1

section .text

main:
    push -11
    call GetStdHandle
    mov [stdout], eax

    push 0
    push written
    push len
    push msg_2
    push qword [stdout]
    call WriteConsoleA
    
    mov eax, 0
    call ExitProcess
