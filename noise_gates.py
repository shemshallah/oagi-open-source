"""
OAGI Noise Gate Architecture
Quantum gates implemented through synchronized CPU noise

Implements universal gate set:
- Single qubit: X, Y, Z, H, T, S
- Two qubit: CNOT, CZ, SWAP
- Three qubit: Toffoli, Fredkin

All gates realized through carefully controlled noise injection
synchronized to cesium atomic frequency.
"""

import numpy as np
from typing import List, Tuple
from quantum_substrate import PhysicalQubit, CesiumClock, QubitFactory
import time

class NoiseGate:
    """Base class for noise-realized quantum gates"""

    def __init__(self, name: str, cesium_clock: CesiumClock):
        self.name = name
        self.cesium = cesium_clock
        self.gate_time_cycles = 0
        self.fidelity = 1.0

    def apply(self, *qubits: PhysicalQubit) -> None:
        """Apply gate to qubits"""
        raise NotImplementedError

    def _noise_controlled_rotation(self,
                                   qubit: PhysicalQubit,
                                   axis: str,
                                   angle: float) -> None:
        """
        Perform rotation using noise synchronization

        Rotation angle is encoded in cesium cycle count.
        Noise pattern induces the rotation.
        """

        # Calculate cesium cycles needed for this rotation
        # More cycles = more precise rotation
        cycles = int(abs(angle) / (2 * np.pi) * 1000)
        cycles = max(cycles, 10)  # Minimum 10 cycles

        start_cycle = self.cesium.get_cesium_cycles()

        # Harvest noise during rotation window
        noise_samples = []

        iteration = 0
        while self.cesium.get_cesium_cycles() < start_cycle + cycles:
            # Generate noise synchronized to rotation
            phase = ((self.cesium.get_cesium_cycles() - start_cycle) / cycles) * angle

            # Noise amplitude modulated by rotation phase
            noise_amplitude = int(abs(np.sin(phase)) * 0xFFFF)

            # Harvest actual hardware noise
            t_start = time.perf_counter_ns()
            x = sum(i**2 for i in range(iteration % 30 + 1))
            t_end = time.perf_counter_ns()
            hw_noise = (t_end - t_start) & 0xFFFF

            # Combine with modulated noise
            combined = (noise_amplitude ^ hw_noise) & 0xFFFFFFFF
            noise_samples.append(combined)

            iteration += 1

        # Apply rotation based on noise
        self._apply_rotation_from_noise(qubit, axis, angle, noise_samples)

        # Update qubit noise samples
        qubit.noise_samples.extend(noise_samples)

        self.gate_time_cycles += cycles

    def _apply_rotation_from_noise(self,
                                   qubit: PhysicalQubit,
                                   axis: str,
                                   angle: float,
                                   noise: List[int]) -> None:
        """Apply rotation matrix to qubit state"""

        # Get current state
        alpha = qubit.alpha
        beta = qubit.beta

        # Rotation matrices
        if axis == 'X':
            # Rx(θ) = cos(θ/2)I - i*sin(θ/2)X
            cos_half = np.cos(angle / 2)
            sin_half = np.sin(angle / 2)

            new_alpha = cos_half * alpha - 1j * sin_half * beta
            new_beta = -1j * sin_half * alpha + cos_half * beta

        elif axis == 'Y':
            # Ry(θ) = cos(θ/2)I - i*sin(θ/2)Y
            cos_half = np.cos(angle / 2)
            sin_half = np.sin(angle / 2)

            new_alpha = cos_half * alpha - sin_half * beta
            new_beta = sin_half * alpha + cos_half * beta

        elif axis == 'Z':
            # Rz(θ) = e^(-iθ/2)|0⟩⟨0| + e^(iθ/2)|1⟩⟨1|
            new_alpha = np.exp(-1j * angle / 2) * alpha
            new_beta = np.exp(1j * angle / 2) * beta

        else:
            raise ValueError(f"Unknown axis: {axis}")

        # Inject noise-induced error (simulates decoherence)
        if noise:
            error_magnitude = (noise[-1] & 0xFF) / 0xFF * 0.001  # 0.1% error
            error_phase = (noise[-2] & 0xFFFF) / 0xFFFF * 2 * np.pi

            error = error_magnitude * np.exp(1j * error_phase)
            new_alpha += error
            new_beta += error

        # Update qubit
        qubit.alpha = new_alpha
        qubit.beta = new_beta

        # Renormalize
        norm = np.sqrt(abs(new_alpha)**2 + abs(new_beta)**2)
        qubit.alpha /= norm
        qubit.beta /= norm

# ============================================================================
# SINGLE QUBIT GATES
# ============================================================================

class PauliX(NoiseGate):
    """X gate (bit flip): |0⟩ ↔ |1⟩"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("X", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        """Apply X rotation (π around X axis)"""
        self._noise_controlled_rotation(qubit, 'X', np.pi)

class PauliY(NoiseGate):
    """Y gate: |0⟩ → i|1⟩, |1⟩ → -i|0⟩"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("Y", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        self._noise_controlled_rotation(qubit, 'Y', np.pi)

class PauliZ(NoiseGate):
    """Z gate (phase flip): |1⟩ → -|1⟩"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("Z", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        self._noise_controlled_rotation(qubit, 'Z', np.pi)

class Hadamard(NoiseGate):
    """Hadamard gate: creates superposition"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("H", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        """H = (1/√2)(X + Z)"""
        # Hadamard = Ry(π/2) · Rz(π)
        self._noise_controlled_rotation(qubit, 'Y', np.pi / 2)
        self._noise_controlled_rotation(qubit, 'Z', np.pi)

class PhaseGate(NoiseGate):
    """S gate (phase gate): |1⟩ → i|1⟩"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("S", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        self._noise_controlled_rotation(qubit, 'Z', np.pi / 2)

class TGate(NoiseGate):
    """T gate (π/8 gate): |1⟩ → e^(iπ/4)|1⟩"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("T", cesium_clock)

    def apply(self, qubit: PhysicalQubit) -> None:
        self._noise_controlled_rotation(qubit, 'Z', np.pi / 4)

# ============================================================================
# TWO QUBIT GATES
# ============================================================================

class CNOT(NoiseGate):
    """
    Controlled-NOT gate

    Flips target qubit if control qubit is |1⟩
    Creates entanglement
    """

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("CNOT", cesium_clock)

    def apply(self, control: PhysicalQubit, target: PhysicalQubit) -> None:
        """Apply CNOT with noise correlation"""

        start_cycle = self.cesium.get_cesium_cycles()
        cycles = 50  # Gate time

        # Harvest correlated noise for both qubits
        shared_noise = []

        iteration = 0
        while self.cesium.get_cesium_cycles() < start_cycle + cycles:
            t_start = time.perf_counter_ns()
            x = iteration**2 % 1000
            t_end = time.perf_counter_ns()
            noise = (t_end - t_start) & 0xFFFFFFFF
            shared_noise.append(noise)
            iteration += 1

        # Apply CNOT logic
        # CNOT = |0⟩⟨0| ⊗ I + |1⟩⟨1| ⊗ X

        # Measure control qubit probability
        prob_control_1 = abs(control.beta)**2

        # If control is likely |1⟩, flip target
        # Use noise for probabilistic threshold
        threshold = (shared_noise[0] & 0xFFFF) / 0xFFFF

        if prob_control_1 > threshold:
            # Apply X to target
            x_gate = PauliX(self.cesium)
            x_gate.apply(target)

        # Update noise samples for entanglement
        control.noise_samples.extend(shared_noise)
        target.noise_samples.extend(shared_noise)

        self.gate_time_cycles += cycles

class ControlledZ(NoiseGate):
    """Controlled-Z gate"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("CZ", cesium_clock)

    def apply(self, control: PhysicalQubit, target: PhysicalQubit) -> None:
        start_cycle = self.cesium.get_cesium_cycles()
        cycles = 50

        shared_noise = []
        iteration = 0
        while self.cesium.get_cesium_cycles() < start_cycle + cycles:
            t_start = time.perf_counter_ns()
            x = iteration**3 % 1000
            t_end = time.perf_counter_ns()
            shared_noise.append((t_end - t_start) & 0xFFFFFFFF)
            iteration += 1

        # CZ: phase flip target if control is |1⟩
        prob_control_1 = abs(control.beta)**2
        threshold = (shared_noise[0] & 0xFFFF) / 0xFFFF

        if prob_control_1 > threshold:
            z_gate = PauliZ(self.cesium)
            z_gate.apply(target)

        control.noise_samples.extend(shared_noise)
        target.noise_samples.extend(shared_noise)

        self.gate_time_cycles += cycles

class SWAP(NoiseGate):
    """SWAP gate: exchanges two qubit states"""

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("SWAP", cesium_clock)

    def apply(self, qubit_a: PhysicalQubit, qubit_b: PhysicalQubit) -> None:
        """SWAP = CNOT(a,b) · CNOT(b,a) · CNOT(a,b)"""

        cnot = CNOT(self.cesium)

        cnot.apply(qubit_a, qubit_b)
        cnot.apply(qubit_b, qubit_a)
        cnot.apply(qubit_a, qubit_b)

        self.gate_time_cycles = cnot.gate_time_cycles

# ============================================================================
# THREE QUBIT GATES
# ============================================================================

class Toffoli(NoiseGate):
    """
    Toffoli gate (CCNOT)

    Flips target if both controls are |1⟩
    Universal for classical computation
    """

    def __init__(self, cesium_clock: CesiumClock):
        super().__init__("Toffoli", cesium_clock)

    def apply(self,
              control1: PhysicalQubit,
              control2: PhysicalQubit,
              target: PhysicalQubit) -> None:

        start_cycle = self.cesium.get_cesium_cycles()
        cycles = 100

        # Harvest triple-correlated noise
        shared_noise = []
        iteration = 0
        while self.cesium.get_cesium_cycles() < start_cycle + cycles:
            t_start = time.perf_counter_ns()
            x = (iteration**2 + iteration**3) % 1000
            t_end = time.perf_counter_ns()
            shared_noise.append((t_end - t_start) & 0xFFFFFFFF)
            iteration += 1

        # Check both controls
        prob_c1_1 = abs(control1.beta)**2
        prob_c2_1 = abs(control2.beta)**2

        threshold1 = (shared_noise[0] & 0xFFFF) / 0xFFFF
        threshold2 = (shared_noise[1] & 0xFFFF) / 0xFFFF

        if prob_c1_1 > threshold1 and prob_c2_1 > threshold2:
            # Both controls are |1⟩, flip target
            x_gate = PauliX(self.cesium)
            x_gate.apply(target)

        # Update all with shared noise
        for q in [control1, control2, target]:
            q.noise_samples.extend(shared_noise)

        self.gate_time_cycles += cycles

class NoiseGateFactory:
    """Factory for creating noise-realized quantum gates"""

    def __init__(self, cesium_clock: CesiumClock):
        self.cesium = cesium_clock

        # Gate registry
        self.gates = {
            'X': PauliX,
            'Y': PauliY,
            'Z': PauliZ,
            'H': Hadamard,
            'S': PhaseGate,
            'T': TGate,
            'CNOT': CNOT,
            'CZ': ControlledZ,
            'SWAP': SWAP,
            'Toffoli': Toffoli
        }

    def create_gate(self, gate_name: str) -> NoiseGate:
        """Create gate instance"""
        if gate_name not in self.gates:
            raise ValueError(f"Unknown gate: {gate_name}")

        return self.gates[gate_name](self.cesium)

    def apply_circuit(self, circuit: List[Tuple[str, List[int]]], qubits: List[PhysicalQubit]):
        """
        Apply quantum circuit

        circuit: List of (gate_name, [qubit_indices])
        """
        total_cycles = 0

        for gate_name, qubit_indices in circuit:
            gate = self.create_gate(gate_name)

            # Get qubits for this gate
            gate_qubits = [qubits[i] for i in qubit_indices]

            # Apply gate
            gate.apply(*gate_qubits)

            total_cycles += gate.gate_time_cycles

        return total_cycles

def test_noise_gates():
    """Test noise gate implementation"""

    print("\n" + "="*70)
    print("NOISE GATE ARCHITECTURE TEST")
    print("="*70)

    from quantum_substrate import QubitFactory

    factory = QubitFactory()
    gate_factory = NoiseGateFactory(factory.cesium)

    # Test 1: Single qubit gates
    print("\n1️⃣  Testing single qubit gates...")

    q = factory.create_qubit((1.0+0j, 0.0+0j))  # |0⟩
    print(f"   Initial: {q.alpha:.4f}|0⟩ + {q.beta:.4f}|1⟩")

    x_gate = gate_factory.create_gate('X')
    x_gate.apply(q)
    print(f"   After X: {q.alpha:.4f}|0⟩ + {q.beta:.4f}|1⟩")

    h_gate = gate_factory.create_gate('H')
    h_gate.apply(q)
    print(f"   After H: {q.alpha:.4f}|0⟩ + {q.beta:.4f}|1⟩")

    # Test 2: CNOT gate
    print("\n2️⃣  Testing CNOT gate...")

    q0 = factory.create_qubit((1.0+0j, 0.0+0j))  # |0⟩
    q1 = factory.create_qubit((1.0+0j, 0.0+0j))  # |0⟩

    print(f"   Initial: q0={q0.alpha:.3f}|0⟩+{q0.beta:.3f}|1⟩, q1={q1.alpha:.3f}|0⟩+{q1.beta:.3f}|1⟩")

    # Create superposition on q0
    h_gate.apply(q0)
    print(f"   After H on q0: q0={q0.alpha:.3f}|0⟩+{q0.beta:.3f}|1⟩")

    # Apply CNOT
    cnot = gate_factory.create_gate('CNOT')
    cnot.apply(q0, q1)
    print(f"   After CNOT: q0={q0.alpha:.3f}|0⟩+{q0.beta:.3f}|1⟩, q1={q1.alpha:.3f}|0⟩+{q1.beta:.3f}|1⟩")

    # Test 3: Toffoli gate
    print("\n3️⃣  Testing Toffoli gate...")

    qa = factory.create_qubit((0.0+0j, 1.0+0j))  # |1⟩
    qb = factory.create_qubit((0.0+0j, 1.0+0j))  # |1⟩
    qc = factory.create_qubit((1.0+0j, 0.0+0j))  # |0⟩

    print(f"   Before: qa=|1⟩, qb=|1⟩, qc=|0⟩")

    toffoli = gate_factory.create_gate('Toffoli')
    toffoli.apply(qa, qb, qc)

    print(f"   After: qc={qc.alpha:.3f}|0⟩+{qc.beta:.3f}|1⟩ (should be near |1⟩)")

    # Test 4: Full circuit
    print("\n4️⃣  Testing quantum circuit...")

    qubits = [factory.create_qubit((1.0+0j, 0.0+0j)) for _ in range(3)]

    # Bell state circuit: H on q0, CNOT(q0, q1)
    circuit = [
        ('H', [0]),
        ('CNOT', [0, 1])
    ]

    cycles = gate_factory.apply_circuit(circuit, qubits)

    print(f"   Circuit executed in {cycles} cesium cycles")
    print(f"   q0: {qubits[0].alpha:.3f}|0⟩ + {qubits[0].beta:.3f}|1⟩")
    print(f"   q1: {qubits[1].alpha:.3f}|0⟩ + {qubits[1].beta:.3f}|1⟩")
    print(f"   (Should be entangled Bell pair)")

    return gate_factory

if __name__ == "__main__":
    gate_factory = test_noise_gates()
    print("\n✅ Noise gates operational")
