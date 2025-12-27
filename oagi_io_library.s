# OAGI I/O Library
# Complete input/output functions in pure assembly

.section .data
    newline: .ascii "\n"
    hex_chars: .ascii "0123456789abcdef"

.section .text

# ============================================================================
# PRINT STRING
# ============================================================================

.globl oagi_print
.globl oagi_println

# void oagi_print(const char *str)
oagi_print:
    push %rbx
    push %r12

    mov %rdi, %r12              # Save string pointer

    # Calculate length
    xor %rbx, %rbx

.print_len_loop:
    cmpb $0, (%r12, %rbx)
    je .print_len_done
    inc %rbx
    jmp .print_len_loop

.print_len_done:
    # write(1, str, len)
    mov $1, %rax                # sys_write
    mov $1, %rdi                # stdout
    mov %r12, %rsi              # string
    mov %rbx, %rdx              # length
    syscall

    pop %r12
    pop %rbx
    ret

# void oagi_println(const char *str)
oagi_println:
    push %rdi
    call oagi_print
    pop %rdi

    # Print newline
    mov $1, %rax
    mov $1, %rdi
    lea newline(%rip), %rsi
    mov $1, %rdx
    syscall

    ret

# ============================================================================
# PRINT INTEGER
# ============================================================================

.globl oagi_print_int
.globl oagi_print_hex

# void oagi_print_int(int64_t value)
oagi_print_int:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp               # Buffer for digits

    mov %rdi, %r10              # Save value
    lea -32(%rbp), %r11         # Buffer start
    mov %r11, %r12              # Current position

    # Handle negative
    test %r10, %r10
    jns .print_int_positive

    # Print minus sign
    movb $'-', (%r12)
    inc %r12
    neg %r10

.print_int_positive:
    mov %r12, %rdi              # Digit start

.print_int_loop:
    xor %rdx, %rdx
    mov %r10, %rax
    mov $10, %rcx
    div %rcx                    # rax = val/10, rdx = val%10

    add $'0', %dl
    movb %dl, (%r12)
    inc %r12

    mov %rax, %r10
    test %r10, %r10
    jnz .print_int_loop

    # Reverse digits
    dec %r12
    mov %rdi, %rsi

.print_int_reverse:
    cmp %rsi, %r12
    jle .print_int_output

    movb (%rsi), %al
    movb (%r12), %cl
    movb %cl, (%rsi)
    movb %al, (%r12)

    inc %rsi
    dec %r12
    jmp .print_int_reverse

.print_int_output:
    # Calculate length
    mov %r12, %rdx
    sub %rdi, %rdx
    inc %rdx

    # write(1, buffer, len)
    mov $1, %rax
    mov $1, %rdi
    mov %rdi, %rsi
    syscall

    leave
    ret

# void oagi_print_hex(uint64_t value)
oagi_print_hex:
    push %rbp
    mov %rsp, %rbp
    sub $32, %rsp

    mov %rdi, %r10              # Value
    lea -32(%rbp), %r11
    mov $0, %r12                # Counter

    # Print "0x" prefix
    movb $'0', (%r11)
    movb $'x', 1(%r11)
    add $2, %r11

.print_hex_loop:
    mov %r10, %rax
    and $0xF, %rax              # Get lowest nibble
    lea hex_chars(%rip), %rcx
    movb (%rcx, %rax), %al
    movb %al, (%r11, %r12)
    inc %r12

    shr $4, %r10
    test %r10, %r10
    jnz .print_hex_loop

    # Reverse hex digits
    mov %r11, %rsi
    lea (%r11, %r12), %rdi
    dec %rdi

.print_hex_reverse:
    cmp %rsi, %rdi
    jle .print_hex_output

    movb (%rsi), %al
    movb (%rdi), %cl
    movb %cl, (%rsi)
    movb %al, (%rdi)

    inc %rsi
    dec %rdi
    jmp .print_hex_reverse

.print_hex_output:
    # Calculate total length (including "0x")
    add $2, %r12

    # write(1, buffer, len)
    mov $1, %rax
    mov $1, %rdi
    lea -32(%rbp), %rsi
    mov %r12, %rdx
    syscall

    leave
    ret

# ============================================================================
# READ INPUT
# ============================================================================

.globl oagi_read_line
.globl oagi_read_int

# ssize_t oagi_read_line(char *buffer, size_t max_len)
oagi_read_line:
    push %rbp
    mov %rsp, %rbp
    push %rbx
    push %r12
    push %r13

    mov %rdi, %r12              # buffer
    mov %rsi, %r13              # max_len
    xor %rbx, %rbx              # bytes read

.read_line_loop:
    # Check if we've reached max length
    cmp %r13, %rbx
    jge .read_line_done

    # read(0, buffer + offset, 1)
    mov $0, %rax                # sys_read
    mov $0, %rdi                # stdin
    lea (%r12, %rbx), %rsi      # buffer + offset
    mov $1, %rdx                # 1 byte
    syscall

    # Check for error or EOF
    test %rax, %rax
    jle .read_line_done

    # Check for newline
    movb (%r12, %rbx), %al
    cmpb $'\n', %al
    je .read_line_done

    inc %rbx
    jmp .read_line_loop

.read_line_done:
    # Null-terminate
    movb $0, (%r12, %rbx)

    # Return bytes read
    mov %rbx, %rax

    pop %r13
    pop %r12
    pop %rbx
    pop %rbp
    ret

# int64_t oagi_read_int(void)
oagi_read_int:
    push %rbp
    mov %rsp, %rbp
    sub $64, %rsp               # Buffer for input

    # Read line
    lea -64(%rbp), %rdi
    mov $63, %rsi
    call oagi_read_line

    # Parse integer
    lea -64(%rbp), %rsi
    xor %rax, %rax              # Result
    xor %rcx, %rcx              # Sign (0=positive, 1=negative)

    # Check for minus sign
    cmpb $'-', (%rsi)
    jne .read_int_parse
    mov $1, %rcx
    inc %rsi

.read_int_parse:
    movb (%rsi), %dl
    test %dl, %dl
    jz .read_int_done

    # Check if digit
    cmpb $'0', %dl
    jb .read_int_done
    cmpb $'9', %dl
    ja .read_int_done

    # result = result * 10 + digit
    imul $10, %rax
    sub $'0', %dl
    movzx %dl, %rdx
    add %rdx, %rax

    inc %rsi
    jmp .read_int_parse

.read_int_done:
    # Apply sign
    test %rcx, %rcx
    jz .read_int_ret
    neg %rax

.read_int_ret:
    leave
    ret

# ============================================================================
# FILE OPERATIONS
# ============================================================================

.globl oagi_file_write
.globl oagi_file_read
.globl oagi_file_exists

# int oagi_file_write(const char *path, const char *data, size_t len)
oagi_file_write:
    push %rbp
    mov %rsp, %rbp
    push %rbx
    push %r12
    push %r13

    mov %rdi, %r12              # path
    mov %rsi, %r13              # data
    mov %rdx, %rbx              # len

    # open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644)
    mov $2, %rax                # sys_open
    mov %r12, %rdi              # pathname
    mov $0x241, %rsi            # O_WRONLY | O_CREAT | O_TRUNC
    mov $0644, %rdx             # mode
    syscall

    # Check for error
    test %rax, %rax
    js .file_write_error

    mov %rax, %r12              # Save fd

    # write(fd, data, len)
    mov $1, %rax                # sys_write
    mov %r12, %rdi              # fd
    mov %r13, %rsi              # buffer
    mov %rbx, %rdx              # count
    syscall

    push %rax                   # Save bytes written

    # close(fd)
    mov $3, %rax                # sys_close
    mov %r12, %rdi
    syscall

    pop %rax                    # Return bytes written
    jmp .file_write_done

.file_write_error:
    mov $-1, %rax

.file_write_done:
    pop %r13
    pop %r12
    pop %rbx
    pop %rbp
    ret

# ssize_t oagi_file_read(const char *path, char *buffer, size_t max_len)
oagi_file_read:
    push %rbp
    mov %rsp, %rbp
    push %rbx
    push %r12
    push %r13

    mov %rdi, %r12              # path
    mov %rsi, %r13              # buffer
    mov %rdx, %rbx              # max_len

    # open(path, O_RDONLY)
    mov $2, %rax                # sys_open
    mov %r12, %rdi
    xor %rsi, %rsi              # O_RDONLY
    xor %rdx, %rdx
    syscall

    test %rax, %rax
    js .file_read_error

    mov %rax, %r12              # Save fd

    # read(fd, buffer, max_len)
    mov $0, %rax                # sys_read
    mov %r12, %rdi
    mov %r13, %rsi
    mov %rbx, %rdx
    syscall

    push %rax                   # Save bytes read

    # close(fd)
    mov $3, %rax                # sys_close
    mov %r12, %rdi
    syscall

    pop %rax
    jmp .file_read_done

.file_read_error:
    mov $-1, %rax

.file_read_done:
    pop %r13
    pop %r12
    pop %rbx
    pop %rbp
    ret

# int oagi_file_exists(const char *path)
oagi_file_exists:
    push %rbp
    mov %rsp, %rbp

    # Try to open file
    mov $2, %rax                # sys_open
    xor %rsi, %rsi              # O_RDONLY
    xor %rdx, %rdx
    syscall

    test %rax, %rax
    js .file_exists_no

    # Close immediately
    mov %rax, %rdi
    mov $3, %rax                # sys_close
    syscall

    mov $1, %rax                # Return 1 (exists)
    jmp .file_exists_done

.file_exists_no:
    xor %rax, %rax              # Return 0 (doesn't exist)

.file_exists_done:
    pop %rbp
    ret
