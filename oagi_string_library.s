# OAGI String Manipulation Library
# Pure assembly string functions

.section .text

# ============================================================================
# STRING LENGTH
# ============================================================================

.globl oagi_strlen

# size_t oagi_strlen(const char *s)
oagi_strlen:
    xor %rax, %rax              # Counter = 0
    test %rdi, %rdi             # Check for NULL
    jz .strlen_done

.strlen_loop:
    cmpb $0, (%rdi, %rax)       # Check for null terminator
    je .strlen_done
    inc %rax
    jmp .strlen_loop

.strlen_done:
    ret

# ============================================================================
# STRING COPY
# ============================================================================

.globl oagi_strcpy

# char *oagi_strcpy(char *dst, const char *src)
oagi_strcpy:
    push %rdi                   # Save dst for return

.strcpy_loop:
    movb (%rsi), %al            # Load byte from src
    movb %al, (%rdi)            # Store to dst
    test %al, %al               # Check for null
    jz .strcpy_done
    inc %rsi
    inc %rdi
    jmp .strcpy_loop

.strcpy_done:
    pop %rax                    # Return original dst
    ret

# ============================================================================
# STRING COMPARE
# ============================================================================

.globl oagi_strcmp

# int oagi_strcmp(const char *s1, const char *s2)
oagi_strcmp:
    xor %rax, %rax

.strcmp_loop:
    movb (%rdi), %al
    movb (%rsi), %cl

    cmp %cl, %al
    jne .strcmp_diff

    test %al, %al               # Check for null
    jz .strcmp_equal

    inc %rdi
    inc %rsi
    jmp .strcmp_loop

.strcmp_diff:
    sub %rcx, %rax
    ret

.strcmp_equal:
    xor %rax, %rax
    ret

# ============================================================================
# MEMORY COPY
# ============================================================================

.globl oagi_memcpy

# void *oagi_memcpy(void *dst, const void *src, size_t n)
oagi_memcpy:
    push %rdi                   # Save dst for return
    mov %rdx, %rcx              # Count
    rep movsb                   # Copy bytes
    pop %rax                    # Return dst
    ret

# ============================================================================
# MEMORY SET
# ============================================================================

.globl oagi_memset

# void *oagi_memset(void *s, int c, size_t n)
oagi_memset:
    push %rdi                   # Save s for return
    mov %sil, %al               # Value to set
    mov %rdx, %rcx              # Count
    rep stosb                   # Set bytes
    pop %rax                    # Return s
    ret

# ============================================================================
# INTEGER TO STRING (decimal)
# ============================================================================

.globl oagi_itoa

# char *oagi_itoa(int64_t value, char *buffer)
oagi_itoa:
    push %rbx
    push %r12
    push %r13

    mov %rdi, %r12              # Save value
    mov %rsi, %r13              # Save buffer
    mov %rsi, %rbx              # Current position

    # Handle negative
    test %r12, %r12
    jns .itoa_positive

    movb $'-', (%rbx)
    inc %rbx
    neg %r12

.itoa_positive:
    # Convert to string (reverse)
    mov %rbx, %rdi              # Start position

.itoa_loop:
    xor %rdx, %rdx
    mov %r12, %rax
    mov $10, %rcx
    div %rcx                    # rax = value / 10, rdx = value % 10

    add $'0', %dl               # Convert to ASCII
    movb %dl, (%rbx)
    inc %rbx

    mov %rax, %r12
    test %r12, %r12
    jnz .itoa_loop

    # Null terminate
    movb $0, (%rbx)

    # Reverse the digits
    dec %rbx
    mov %rdi, %rsi              # Start

.itoa_reverse:
    cmp %rsi, %rbx
    jle .itoa_done

    movb (%rsi), %al
    movb (%rbx), %cl
    movb %cl, (%rsi)
    movb %al, (%rbx)

    inc %rsi
    dec %rbx
    jmp .itoa_reverse

.itoa_done:
    mov %r13, %rax              # Return buffer
    pop %r13
    pop %r12
    pop %rbx
    ret
