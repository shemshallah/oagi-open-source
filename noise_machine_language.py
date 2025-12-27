"""
OAGI Noise Machine Language (NML)
Assembly-like language for programming with noise gates

Syntax:
    LABEL:
        GATE qubit_reg, ...
        MEASURE qubit_reg -> classical_reg
        JUMP LABEL
        CJUMP classical_reg, LABEL
        HALT

Example program:
    START:
        H q0           # Hadamard on qubit 0
        CNOT q0, q1    # Entangle
        MEASURE q0 -> c0
        CJUMP c0, ONE
    ZERO:
        X q1
        HALT
    ONE:
        Z q1
        HALT
"""

import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class NoiseOpcode(Enum):
    """Noise machine language opcodes"""
    # Single qubit gates
    X = "X"
    Y = "Y"
    Z = "Z"
    H = "H"
    S = "S"
    T = "T"

    # Two qubit gates
    CNOT = "CNOT"
    CZ = "CZ"
    SWAP = "SWAP"

    # Three qubit gates
    TOFFOLI = "TOFFOLI"

    # Measurement
    MEASURE = "MEASURE"

    # Control flow
    JUMP = "JUMP"
    CJUMP = "CJUMP"
    CALL = "CALL"
    RET = "RET"
    HALT = "HALT"

    # Jitter control
    HARVEST = "HARVEST"  # Harvest jitter into qubit
    INJECT = "INJECT"    # Inject noise pattern
    SYNC = "SYNC"        # Synchronize to cesium

@dataclass
class NoiseInstruction:
    """Single NML instruction"""
    opcode: NoiseOpcode
    operands: List[str]
    label: Optional[str] = None
    line_number: int = 0

class NoiseAssembler:
    """Assembles NML source code into executable form"""

    def __init__(self):
        self.labels: Dict[str, int] = {}
        self.instructions: List[NoiseInstruction] = []

    def parse(self, source: str) -> List[NoiseInstruction]:
        """Parse NML source code"""

        self.labels.clear()
        self.instructions.clear()

        lines = source.strip().split('\n')
        instruction_index = 0

        for line_num, line in enumerate(lines, 1):
            # Remove comments
            if '#' in line:
                line = line[:line.index('#')]

            line = line.strip()
            if not line:
                continue

            # Check for label
            if ':' in line:
                label_part, rest = line.split(':', 1)
                label = label_part.strip()
                self.labels[label] = instruction_index
                line = rest.strip()

                if not line:
                    continue

            # Parse instruction
            parts = re.split(r'[,\s]+', line)
            opcode_str = parts[0].upper()

            try:
                opcode = NoiseOpcode(opcode_str)
            except ValueError:
                print(f"Warning: Unknown opcode '{opcode_str}' at line {line_num}")
                continue

            operands = [p.strip() for p in parts[1:] if p.strip()]

            instr = NoiseInstruction(
                opcode=opcode,
                operands=operands,
                line_number=line_num
            )

            self.instructions.append(instr)
            instruction_index += 1

        return self.instructions

    def assemble_to_bytecode(self) -> bytes:
        """Convert instructions to bytecode"""

        bytecode = bytearray()

        # Header
        bytecode.extend(b'NML1')  # Magic number
        bytecode.extend(len(self.instructions).to_bytes(4, 'little'))

        # Label table
        bytecode.extend(len(self.labels).to_bytes(2, 'little'))
        for label, addr in self.labels.items():
            label_bytes = label.encode('utf-8')
            bytecode.append(len(label_bytes))
            bytecode.extend(label_bytes)
            bytecode.extend(addr.to_bytes(4, 'little'))

        # Instructions
        for instr in self.instructions:
            # Opcode (1 byte)
            bytecode.append(list(NoiseOpcode).index(instr.opcode))

            # Number of operands (1 byte)
            bytecode.append(len(instr.operands))

            # Operands
            for operand in instr.operands:
                op_bytes = operand.encode('utf-8')
                bytecode.append(len(op_bytes))
                bytecode.extend(op_bytes)

        return bytes(bytecode)

class NoiseVM:
    """
    Virtual machine for executing Noise Machine Language

    Executes NML programs on physical qubits
    """

    def __init__(self, qubit_factory, gate_factory, qram):
        self.factory = qubit_factory
        self.gates = gate_factory
        self.qram = qram

        # Registers
        self.qubit_registers: Dict[str, int] = {}  # qubit name -> qubit index
        self.classical_registers: Dict[str, int] = {}

        # Program state
        self.instructions: List[NoiseInstruction] = []
        self.labels: Dict[str, int] = {}
        self.pc = 0  # Program counter
        self.halted = False

        # Call stack
        self.call_stack: List[int] = []

    def load_program(self, instructions: List[NoiseInstruction], labels: Dict[str, int]):
        """Load assembled program"""
        self.instructions = instructions
        self.labels = labels
        self.pc = 0
        self.halted = False

    def allocate_qubit(self, reg_name: str) -> int:
        """Allocate a physical qubit for register"""
        if reg_name in self.qubit_registers:
            return self.qubit_registers[reg_name]

        qubit = self.factory.create_qubit()
        self.qubit_registers[reg_name] = qubit.index
        return qubit.index

    def get_qubit(self, reg_name: str):
        """Get qubit object from register name"""
        if reg_name not in self.qubit_registers:
            self.allocate_qubit(reg_name)

        qubit_idx = self.qubit_registers[reg_name]

        # Find qubit in factory
        # (In real implementation, would have qubit manager)
        return self.factory.create_qubit()  # Simplified

    def execute_instruction(self, instr: NoiseInstruction):
        """Execute single instruction"""

        opcode = instr.opcode
        operands = instr.operands

        # Single qubit gates
        if opcode in [NoiseOpcode.X, NoiseOpcode.Y, NoiseOpcode.Z,
                     NoiseOpcode.H, NoiseOpcode.S, NoiseOpcode.T]:
            qubit = self.get_qubit(operands[0])
            gate = self.gates.create_gate(opcode.value)
            gate.apply(qubit)

        # Two qubit gates
        elif opcode in [NoiseOpcode.CNOT, NoiseOpcode.CZ, NoiseOpcode.SWAP]:
            q1 = self.get_qubit(operands[0])
            q2 = self.get_qubit(operands[1])
            gate = self.gates.create_gate(opcode.value)
            gate.apply(q1, q2)

        # Three qubit gates
        elif opcode == NoiseOpcode.TOFFOLI:
            q1 = self.get_qubit(operands[0])
            q2 = self.get_qubit(operands[1])
            q3 = self.get_qubit(operands[2])
            gate = self.gates.create_gate(opcode.value)
            gate.apply(q1, q2, q3)

        # Measurement
        elif opcode == NoiseOpcode.MEASURE:
            qubit_reg = operands[0]
            classical_reg = operands[2]  # Skip '->'

            qubit = self.get_qubit(qubit_reg)
            result = qubit.measure()

            self.classical_registers[classical_reg] = result

        # Control flow
        elif opcode == NoiseOpcode.JUMP:
            target_label = operands[0]
            self.pc = self.labels[target_label]
            return  # Don't increment PC

        elif opcode == NoiseOpcode.CJUMP:
            condition_reg = operands[0]
            target_label = operands[1]

            if self.classical_registers.get(condition_reg, 0) == 1:
                self.pc = self.labels[target_label]
                return

        elif opcode == NoiseOpcode.CALL:
            target_label = operands[0]
            self.call_stack.append(self.pc + 1)
            self.pc = self.labels[target_label]
            return

        elif opcode == NoiseOpcode.RET:
            if self.call_stack:
                self.pc = self.call_stack.pop()
                return

        elif opcode == NoiseOpcode.HALT:
            self.halted = True
            return

        # Jitter control
        elif opcode == NoiseOpcode.HARVEST:
            qubit_reg = operands[0]
            cycles = int(operands[1]) if len(operands) > 1 else 100

            # Harvest jitter and initialize qubit
            from quantum_substrate import NoiseHarvester
            harvester = NoiseHarvester(self.factory.cesium)
            noise = harvester.harvest_cycle(cycles)
            alpha, beta = harvester.noise_to_qubit_state(noise)

            qubit = self.get_qubit(qubit_reg)
            qubit.alpha = alpha
            qubit.beta = beta

        elif opcode == NoiseOpcode.SYNC:
            cycles = int(operands[0]) if operands else 1000
            self.factory.cesium.wait_cesium_cycles(cycles)

        # Increment PC
        self.pc += 1

    def run(self, max_steps: int = 10000) -> Dict:
        """Run program to completion"""

        step = 0
        while not self.halted and self.pc < len(self.instructions) and step < max_steps:
            instr = self.instructions[self.pc]
            self.execute_instruction(instr)
            step += 1

        return {
            'steps': step,
            'halted': self.halted,
            'classical_registers': dict(self.classical_registers),
            'qubit_registers': list(self.qubit_registers.keys())
        }

# ============================================================================
# Example Programs
# ============================================================================

BELL_STATE_PROGRAM = """
# Create Bell state (|00⟩ + |11⟩)/√2

MAIN:
    H q0              # Create superposition
    CNOT q0, q1       # Entangle
    HALT
"""

TELEPORTATION_PROGRAM = """
# Quantum teleportation protocol

SETUP:
    # Create entangled pair between Alice and Bob
    H q1
    CNOT q1, q2

    # Alice has unknown state in q0 and half of entangled pair in q1
    # Bob has other half in q2

ALICE_MEASURE:
    CNOT q0, q1
    H q0
    MEASURE q0 -> c0
    MEASURE q1 -> c1

BOB_CORRECT:
    CJUMP c1, BOB_X
BOB_CHECK_Z:
    CJUMP c0, BOB_Z
    JUMP DONE

BOB_X:
    X q2
    CJUMP c0, BOB_Z
    JUMP DONE

BOB_Z:
    Z q2

DONE:
    HALT
"""

GROVER_SEARCH_PROGRAM = """
# Grover's algorithm (2-qubit version)

INIT:
    H q0
    H q1

ORACLE:
    # Mark state |11⟩
    CZ q0, q1

DIFFUSION:
    # Diffusion operator
    H q0
    H q1
    X q0
    X q1
    CZ q0, q1
    X q0
    X q1
    H q0
    H q1

MEASURE_RESULT:
    MEASURE q0 -> c0
    MEASURE q1 -> c1
    HALT
"""

def test_noise_machine_language():
    """Test NML assembler and VM"""

    print("\n" + "="*70)
    print("NOISE MACHINE LANGUAGE TEST")
    print("="*70)

    # Test assembler
    print("\n1️⃣  Testing assembler...")

    assembler = NoiseAssembler()
    instructions = assembler.parse(BELL_STATE_PROGRAM)

    print(f"   Assembled {len(instructions)} instructions")
    print(f"   Labels: {assembler.labels}")

    for i, instr in enumerate(instructions):
        print(f"   [{i}] {instr.opcode.value} {', '.join(instr.operands)}")

    # Test bytecode generation
    print("\n2️⃣  Testing bytecode generation...")

    bytecode = assembler.assemble_to_bytecode()
    print(f"   Generated {len(bytecode)} bytes")
    print(f"   Magic: {bytecode[:4]}")

    # Test VM execution
    print("\n3️⃣  Testing VM execution...")

    from quantum_substrate import QubitFactory
    from noise_gates import NoiseGateFactory
    from moonshine_lattice import MoonshineLattice
    from lattice_qram import LatticeQRAM

    factory = QubitFactory()
    gate_factory = NoiseGateFactory(factory.cesium)
    lattice = MoonshineLattice(truncated_dimension=128)
    qram = LatticeQRAM(capacity=8, qubit_factory=factory, lattice=lattice)

    vm = NoiseVM(factory, gate_factory, qram)
    vm.load_program(instructions, assembler.labels)

    result = vm.run()

    print(f"   Execution complete:")
    print(f"   Steps: {result['steps']}")
    print(f"   Halted: {result['halted']}")
    print(f"   Classical registers: {result['classical_registers']}")
    print(f"   Qubit registers: {result['qubit_registers']}")

    return vm

if __name__ == "__main__":
    vm = test_noise_machine_language()
    print("\n✅ Noise Machine Language operational")
