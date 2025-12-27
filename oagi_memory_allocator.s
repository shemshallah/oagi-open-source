# OAGI Memory Allocator
# Pure assembly implementation of malloc/free
# Uses mmap for large allocations, custom heap for small ones

.section .data
    heap_start: .quad 0         # Start of heap
    heap_current: .quad 0       # Current heap pointer
    heap_end: .quad 0           # End of heap

    # Memory block header structure (16 bytes)
    # [0-7]: size
    # [8-15]: flags (bit 0: allocated)

.section .text

# ============================================================================
# HEAP INITIALIZATION
# ============================================================================

.globl oagi_heap_init

# void oagi_heap_init(size_t initial_size)
oagi_heap_init:
    push %rbp
    mov %rsp, %rbp
    push %rbx

    # Save requested size
    mov %rdi, %rbx

    # Round up to page size (4096)
    add $4095, %rbx
    and $-4096, %rbx

    # mmap(NULL, size, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0)
    xor %rdi, %rdi              # addr = NULL
    mov %rbx, %rsi              # length
    mov $3, %rdx                # PROT_READ | PROT_WRITE
    mov $34, %r10               # MAP_PRIVATE | MAP_ANONYMOUS
    mov $-1, %r8                # fd = -1
    xor %r9, %r9                # offset = 0
    mov $9, %rax                # sys_mmap
    syscall

    # Check for error
    cmp $-4096, %rax
    jae .heap_init_error

    # Store heap boundaries
    mov %rax, heap_start(%rip)
    mov %rax, heap_current(%rip)
    add %rbx, %rax
    mov %rax, heap_end(%rip)

    xor %rax, %rax              # Return 0 (success)
    jmp .heap_init_done

.heap_init_error:
    mov $-1, %rax               # Return -1 (error)

.heap_init_done:
    pop %rbx
    pop %rbp
    ret

# ============================================================================
# MALLOC - Allocate Memory
# ============================================================================

.globl oagi_malloc

# void *oagi_malloc(size_t size)
oagi_malloc:
    push %rbp
    mov %rsp, %rbp
    push %rbx
    push %r12

    # Save requested size
    mov %rdi, %r12

    # Add header size (16 bytes)
    add $16, %r12

    # Align to 16 bytes
    add $15, %r12
    and $-16, %r12

    # Check if heap initialized
    mov heap_start(%rip), %rax
    test %rax, %rax
    jz .malloc_init_heap

.malloc_check_space:
    # Check if we have space in current heap
    mov heap_current(%rip), %rbx
    mov %rbx, %rax
    add %r12, %rax
    cmp heap_end(%rip), %rax
    ja .malloc_expand_heap

    # We have space - allocate from current heap
    mov heap_current(%rip), %rax

    # Write header
    mov %r12, (%rax)            # size
    movq $1, 8(%rax)            # flags: allocated

    # Update heap_current
    mov %rax, %rbx
    add %r12, %rbx
    mov %rbx, heap_current(%rip)

    # Return pointer to data (skip header)
    add $16, %rax
    jmp .malloc_done

.malloc_init_heap:
    # Initialize heap with 1MB
    mov $1048576, %rdi
    call oagi_heap_init
    test %rax, %rax
    jnz .malloc_error
    jmp .malloc_check_space

.malloc_expand_heap:
    # For large allocations, use mmap directly
    cmp $65536, %r12            # If > 64KB
    ja .malloc_mmap

    # Expand heap with another 1MB
    mov $1048576, %rdi
    call oagi_heap_init
    test %rax, %rax
    jnz .malloc_error
    jmp .malloc_check_space

.malloc_mmap:
    # Direct mmap for large allocation
    xor %rdi, %rdi              # addr = NULL
    mov %r12, %rsi              # length
    mov $3, %rdx                # PROT_READ | PROT_WRITE
    mov $34, %r10               # MAP_PRIVATE | MAP_ANONYMOUS
    mov $-1, %r8                # fd = -1
    xor %r9, %r9                # offset = 0
    mov $9, %rax                # sys_mmap
    syscall

    cmp $-4096, %rax
    jae .malloc_error

    # Write header
    mov %r12, (%rax)
    movq $1, 8(%rax)

    add $16, %rax
    jmp .malloc_done

.malloc_error:
    xor %rax, %rax              # Return NULL

.malloc_done:
    pop %r12
    pop %rbx
    pop %rbp
    ret

# ============================================================================
# FREE - Deallocate Memory
# ============================================================================

.globl oagi_free

# void oagi_free(void *ptr)
oagi_free:
    push %rbp
    mov %rsp, %rbp

    # Check for NULL
    test %rdi, %rdi
    jz .free_done

    # Get header address
    sub $16, %rdi

    # Read size
    mov (%rdi), %rsi

    # Check if large allocation (>64KB)
    cmp $65536, %rsi
    ja .free_mmap

    # Mark as free
    movq $0, 8(%rdi)
    jmp .free_done

.free_mmap:
    # munmap(ptr, size)
    mov $11, %rax               # sys_munmap
    syscall

.free_done:
    pop %rbp
    ret

# ============================================================================
# CALLOC - Allocate and Zero Memory
# ============================================================================

.globl oagi_calloc

# void *oagi_calloc(size_t nmemb, size_t size)
oagi_calloc:
    push %rbp
    mov %rsp, %rbp
    push %rbx

    # Calculate total size
    mov %rdi, %rax
    mul %rsi                    # rax = nmemb * size
    mov %rax, %rbx

    # Allocate
    mov %rax, %rdi
    call oagi_malloc

    # Check for NULL
    test %rax, %rax
    jz .calloc_done

    # Zero memory
    mov %rax, %rdi
    mov %rbx, %rcx
    xor %rax, %rax
    rep stosb

    mov %rdi, %rax

.calloc_done:
    pop %rbx
    pop %rbp
    ret
