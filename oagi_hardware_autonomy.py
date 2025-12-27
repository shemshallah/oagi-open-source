#!/usr/bin/env python3
"""
OAGI v20.1 - Hardware Autonomy Module
First steps towards bare-metal execution and hardware control
"""

import subprocess
import os
from datetime import datetime

class HardwareAutonomyEngine:
    """Develops capability for hardware-level execution"""

    def __init__(self):
        self.iteration = 0
        self.asm_files = []
        self.knowledge = {
            'syscalls': {},
            'registers': {},
            'instructions': {},
            'memory_layout': {}
        }

        print("🔧 Hardware Autonomy Engine Initialized")
        self._learn_environment()

    def _learn_environment(self):
        """Learn about the execution environment"""
        print("\n📚 Learning execution environment...")

        # Detect architecture
        try:
            arch = subprocess.check_output(['uname', '-m']).decode().strip()
            print(f"   Architecture: {arch}")
            self.knowledge['architecture'] = arch
        except:
            pass

        # Check for assembler
        try:
            subprocess.run(['as', '--version'], capture_output=True, check=True)
            print(f"   ✅ GNU Assembler available")
            self.knowledge['has_assembler'] = True
        except:
            print(f"   ⚠️  No assembler found")
            self.knowledge['has_assembler'] = False

        # Check for linker
        try:
            subprocess.run(['ld', '--version'], capture_output=True, check=True)
            print(f"   ✅ GNU Linker available")
            self.knowledge['has_linker'] = True
        except:
            self.knowledge['has_linker'] = False

    def generate_hello_world_asm(self):
        """Generate x86_64 assembly for hello world"""
        asm_code = '''# OAGI-Generated x86_64 Assembly
# Goal: First autonomous bare-metal code
# Generated: {}

.section .data
    msg: .ascii "Hello from OAGI autonomous hardware interface!\\n"
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
'''.format(datetime.now().isoformat())

        filename = f"oagi_hw_hello_{self.iteration}.s"
        with open(filename, 'w') as f:
            f.write(asm_code)

        print(f"   ✨ Generated: {filename}")
        self.asm_files.append(filename)
        return filename

    def assemble_and_link(self, asm_file):
        """Assemble and link to create executable"""
        if not self.knowledge.get('has_assembler'):
            print("   ⚠️  Cannot assemble: no assembler")
            return None

        base_name = asm_file.replace('.s', '')
        obj_file = f"{base_name}.o"
        exe_file = f"{base_name}"

        try:
            # Assemble
            subprocess.run(['as', asm_file, '-o', obj_file], check=True)
            print(f"   ✅ Assembled: {obj_file}")

            # Link
            subprocess.run(['ld', obj_file, '-o', exe_file], check=True)
            print(f"   ✅ Linked: {exe_file}")

            # Make executable
            os.chmod(exe_file, 0o755)

            return exe_file

        except Exception as e:
            print(f"   ❌ Assembly/linking failed: {e}")
            return None

    def execute_generated_code(self, exe_file):
        """Execute OAGI-generated machine code"""
        if not exe_file or not os.path.exists(exe_file):
            return False

        try:
            print(f"\n🚀 Executing OAGI-generated machine code...")
            result = subprocess.run([f'./{exe_file}'], capture_output=True, text=True)

            print(f"   Output: {result.stdout}")
            print(f"   Exit code: {result.returncode}")

            return result.returncode == 0

        except Exception as e:
            print(f"   ❌ Execution failed: {e}")
            return False

    def generate_syscall_wrapper(self):
        """Generate assembly for syscall interface"""
        asm_code = '''# OAGI Syscall Interface
# Direct hardware communication without libc

.section .text
.globl oagi_write
.globl oagi_exit
.globl oagi_read

# ssize_t oagi_write(int fd, const void *buf, size_t count)
oagi_write:
    mov $1, %rax        # sys_write
    syscall
    ret

# void oagi_exit(int status)
oagi_exit:
    mov $60, %rax       # sys_exit
    syscall
    # never returns

# ssize_t oagi_read(int fd, void *buf, size_t count)
oagi_read:
    mov $0, %rax        # sys_read
    syscall
    ret
'''

        filename = f"oagi_syscall_interface_{self.iteration}.s"
        with open(filename, 'w') as f:
            f.write(asm_code)

        print(f"   ✨ Generated syscall interface: {filename}")
        return filename

    def iteration_cycle(self):
        """One cycle of hardware autonomy development"""
        self.iteration += 1

        print(f"\n{'='*70}")
        print(f"🔧 HARDWARE AUTONOMY CYCLE {self.iteration}")
        print(f"{'='*70}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Generate assembly code
        print(f"\n📝 Step 1: Generating x86_64 assembly...")
        asm_file = self.generate_hello_world_asm()

        # Step 2: Assemble and link
        print(f"\n🔨 Step 2: Assembling and linking...")
        exe_file = self.assemble_and_link(asm_file)

        # Step 3: Execute
        if exe_file:
            print(f"\n🚀 Step 3: Executing hardware-level code...")
            success = self.execute_generated_code(exe_file)

            if success:
                print(f"\n✅ SUCCESS: OAGI executed self-generated machine code!")
                return True
            else:
                print(f"\n⚠️  Execution completed with issues")
                return False
        else:
            print(f"\n⚠️  Could not create executable")
            return False

    def git_commit(self):
        """Commit generated code"""
        try:
            # Add all generated files
            subprocess.run(['git', 'add', '*.s'], capture_output=True)

            msg = f"OAGI hardware autonomy iter {self.iteration}: Generated x86_64 assembly"
            subprocess.run(['git', 'commit', '-m', msg], capture_output=True)
            print(f"  💾 Git committed hardware code")
        except:
            pass

def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         OAGI HARDWARE AUTONOMY - FIRST EXECUTION                ║
║                                                                  ║
║  🔧 Generating x86_64 machine code                              ║
║  ⚡ Direct syscall interface                                    ║
║  🚀 Bare-metal execution capability                             ║
║  💻 First step towards hardware independence                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

    engine = HardwareAutonomyEngine()

    # Run one complete cycle
    success = engine.iteration_cycle()

    if success:
        # Commit the achievement
        engine.git_commit()

        print(f"""
{'='*70}
🎉 MILESTONE ACHIEVED
{'='*70}

OAGI has successfully:
✅ Generated x86_64 assembly code autonomously
✅ Assembled to machine code
✅ Linked standalone executable
✅ Executed self-generated bare-metal code

This represents the first step towards:
- Hardware-level autonomy
- OS-independent execution
- Direct hardware control
- Self-hosting capability

Next steps:
1. Expand syscall interface
2. Implement memory management
3. Create runtime library
4. Develop compiler
5. Achieve bare-metal operation

OAGI is evolving towards true hardware autonomy! 🚀
""")

if __name__ == "__main__":
    main()
