# OAGI-Generated x86_64 Assembly
# Goal: First autonomous bare-metal code
# Generated: 2025-12-27T17:44:36.519203

.section .data
    msg: .ascii "Hello from OAGI autonomous hardware interface!\n"
    msg_len = . - msg

.section .text
.globl _start

_start:
    # write(1, msg, msg_len)
    mov $1, %rax        # syscall number (sys_write)
    mov $1, %rdi        # file descriptor (stdout)
    lea msg(%rip), %rsi # message address
    mov $msg_len, %rdx  # message length
    syscall

    # exit(0)
    mov $60, %rax       # syscall number (sys_exit)
    xor %rdi, %rdi      # exit code 0
    syscall
