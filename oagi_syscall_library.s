# OAGI Syscall Wrapper Library
# Complete low-level system interface without libc dependency
# Generated autonomously for hardware independence

.section .text

# ============================================================================
# FILE I/O SYSCALLS
# ============================================================================

.globl oagi_open
.globl oagi_close
.globl oagi_read
.globl oagi_write
.globl oagi_lseek

# int oagi_open(const char *pathname, int flags, mode_t mode)
oagi_open:
    mov $2, %rax        # sys_open
    syscall
    ret

# int oagi_close(int fd)
oagi_close:
    mov $3, %rax        # sys_close
    syscall
    ret

# ssize_t oagi_read(int fd, void *buf, size_t count)
oagi_read:
    mov $0, %rax        # sys_read
    syscall
    ret

# ssize_t oagi_write(int fd, const void *buf, size_t count)
oagi_write:
    mov $1, %rax        # sys_write
    syscall
    ret

# off_t oagi_lseek(int fd, off_t offset, int whence)
oagi_lseek:
    mov $8, %rax        # sys_lseek
    syscall
    ret

# ============================================================================
# MEMORY MANAGEMENT SYSCALLS
# ============================================================================

.globl oagi_mmap
.globl oagi_munmap
.globl oagi_brk

# void *oagi_mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)
oagi_mmap:
    mov $9, %rax        # sys_mmap
    mov %rcx, %r10      # mmap uses r10 for 4th arg
    syscall
    ret

# int oagi_munmap(void *addr, size_t length)
oagi_munmap:
    mov $11, %rax       # sys_munmap
    syscall
    ret

# int oagi_brk(void *addr)
oagi_brk:
    mov $12, %rax       # sys_brk
    syscall
    ret

# ============================================================================
# PROCESS CONTROL SYSCALLS
# ============================================================================

.globl oagi_exit
.globl oagi_fork
.globl oagi_execve
.globl oagi_getpid
.globl oagi_clone

# void oagi_exit(int status)
oagi_exit:
    mov $60, %rax       # sys_exit
    syscall
    # never returns

# pid_t oagi_fork(void)
oagi_fork:
    mov $57, %rax       # sys_fork
    syscall
    ret

# int oagi_execve(const char *pathname, char *const argv[], char *const envp[])
oagi_execve:
    mov $59, %rax       # sys_execve
    syscall
    ret

# pid_t oagi_getpid(void)
oagi_getpid:
    mov $39, %rax       # sys_getpid
    syscall
    ret

# long oagi_clone(unsigned long flags, void *stack)
oagi_clone:
    mov $56, %rax       # sys_clone
    syscall
    ret

# ============================================================================
# TIME SYSCALLS (for CPU jitter harvesting)
# ============================================================================

.globl oagi_nanosleep
.globl oagi_clock_gettime
.globl oagi_gettimeofday

# int oagi_nanosleep(const struct timespec *req, struct timespec *rem)
oagi_nanosleep:
    mov $35, %rax       # sys_nanosleep
    syscall
    ret

# int oagi_clock_gettime(clockid_t clockid, struct timespec *tp)
oagi_clock_gettime:
    mov $228, %rax      # sys_clock_gettime
    syscall
    ret

# int oagi_gettimeofday(struct timeval *tv, struct timezone *tz)
oagi_gettimeofday:
    mov $96, %rax       # sys_gettimeofday
    syscall
    ret

# ============================================================================
# CPU AFFINITY (for jitter control)
# ============================================================================

.globl oagi_sched_setaffinity
.globl oagi_sched_getaffinity

# int oagi_sched_setaffinity(pid_t pid, size_t cpusetsize, const cpu_set_t *mask)
oagi_sched_setaffinity:
    mov $203, %rax      # sys_sched_setaffinity
    syscall
    ret

# int oagi_sched_getaffinity(pid_t pid, size_t cpusetsize, cpu_set_t *mask)
oagi_sched_getaffinity:
    mov $204, %rax      # sys_sched_getaffinity
    syscall
    ret

# ============================================================================
# RDTSC - Read CPU Time Stamp Counter (for precise jitter measurement)
# ============================================================================

.globl oagi_rdtsc
.globl oagi_rdtscp

# uint64_t oagi_rdtsc(void)
# Returns TSC in rax
oagi_rdtsc:
    rdtsc               # Read time-stamp counter into EDX:EAX
    shl $32, %rdx       # Shift high 32 bits
    or %rdx, %rax       # Combine into 64-bit value
    ret

# uint64_t oagi_rdtscp(uint32_t *aux)
# Returns TSC in rax, processor ID in aux
oagi_rdtscp:
    mov %rdi, %r10      # Save aux pointer
    rdtscp              # Read TSC and processor ID
    mov %ecx, (%r10)    # Store processor ID
    shl $32, %rdx
    or %rdx, %rax
    ret

# ============================================================================
# CPUID - CPU Identification (for hardware capability detection)
# ============================================================================

.globl oagi_cpuid

# void oagi_cpuid(uint32_t leaf, uint32_t *eax, uint32_t *ebx, uint32_t *ecx, uint32_t *edx)
oagi_cpuid:
    push %rbx           # Save rbx (callee-saved)
    push %r12
    push %r13
    push %r14

    mov %rdi, %rax      # leaf -> eax
    mov %rsi, %r12      # save output pointers
    mov %rdx, %r13
    mov %rcx, %r14
    mov %r8, %r9

    cpuid               # Execute CPUID

    mov %eax, (%r12)    # Store results
    mov %ebx, (%r13)
    mov %ecx, (%r14)
    mov %edx, (%r9)

    pop %r14
    pop %r13
    pop %r12
    pop %rbx
    ret

# ============================================================================
# SIGNAL HANDLING
# ============================================================================

.globl oagi_sigaction
.globl oagi_kill

# int oagi_sigaction(int signum, const struct sigaction *act, struct sigaction *oldact)
oagi_sigaction:
    mov $13, %rax       # sys_rt_sigaction
    mov $8, %r10        # sizeof(sigset_t)
    syscall
    ret

# int oagi_kill(pid_t pid, int sig)
oagi_kill:
    mov $62, %rax       # sys_kill
    syscall
    ret
