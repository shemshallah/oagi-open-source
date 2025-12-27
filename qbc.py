#!/usr/bin/env python3
"""
QBC (Quantum-Bit-Classical) Encoding System

Provides bidirectional translation between:
- Quantum states (qubits with complex amplitudes)
- Classical bits (binary 0/1)
- Noise-mediated encoding

Uses CPU noise as the physical medium for encoding/decoding.
"""

import time
import struct
import numpy as np
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


@dataclass
class QBCState:
    """Quantum-Bit-Classical state representation"""
    quantum_amplitude_alpha: complex  # |0⟩ amplitude
    quantum_amplitude_beta: complex   # |1⟩ amplitude
    classical_bit: int  # 0 or 1
    noise_signature: List[int]  # Hardware noise anchor
    coherence_quality: float  # 0.0 to 1.0
    timestamp_ns: int


class NoiseEncoder:
    """Encodes classical bits into noise patterns"""

    def __init__(self):
        self.encoding_cache: Dict[int, List[int]] = {}

    def encode_bit(self, bit: int, noise_samples: int = 256) -> List[int]:
        """Encode a classical bit (0 or 1) into noise pattern"""
        noise_pattern = []

        for i in range(noise_samples):
            # Harvest timing noise
            t_start = time.perf_counter_ns()
            # Variable workload based on bit value
            if bit == 0:
                x = sum(j**2 for j in range(i % 20 + 1))
            else:
                x = sum(j**3 for j in range(i % 20 + 1))
            t_end = time.perf_counter_ns()

            jitter = (t_end - t_start) & 0xFFFF
            noise_pattern.append(jitter)

        return noise_pattern

    def decode_pattern(self, noise_pattern: List[int]) -> int:
        """Decode noise pattern back to classical bit"""
        if not noise_pattern:
            return 0

        # Analyze noise variance
        mean_noise = sum(noise_pattern) / len(noise_pattern)
        variance = sum((x - mean_noise)**2 for x in noise_pattern) / len(noise_pattern)

        # Higher variance indicates bit=1 (more complex computation)
        threshold = 1000.0
        return 1 if variance > threshold else 0


class QuantumBitEncoder:
    """Encodes classical bits as quantum states"""

    def bit_to_quantum(self, bit: int, noise_samples: List[int]) -> Tuple[complex, complex]:
        """
        Convert classical bit to quantum amplitudes

        bit=0: |ψ⟩ = |0⟩ (alpha=1, beta=0)
        bit=1: |ψ⟩ = |1⟩ (alpha=0, beta=1)

        Noise adds phase rotation
        """
        if bit == 0:
            alpha = 1.0 + 0j
            beta = 0.0 + 0j
        else:
            alpha = 0.0 + 0j
            beta = 1.0 + 0j

        # Add noise-induced phase
        if noise_samples:
            phase = (sum(noise_samples[:8]) % 360) * np.pi / 180.0
            alpha *= np.exp(1j * phase / 2)
            beta *= np.exp(1j * phase / 2)

        return alpha, beta

    def quantum_to_bit(self, alpha: complex, beta: complex) -> int:
        """Convert quantum state to classical bit via measurement"""
        prob_0 = abs(alpha)**2
        prob_1 = abs(beta)**2

        # Normalize
        total = prob_0 + prob_1
        if total > 0:
            prob_0 /= total

        # Measurement: use hardware noise as randomness source
        t = time.perf_counter_ns()
        random_val = (t & 0xFFFFFFFF) / 0xFFFFFFFF

        return 0 if random_val < prob_0 else 1


class QBCEncoder:
    """Complete Quantum-Bit-Classical encoding system"""

    def __init__(self):
        self.noise_encoder = NoiseEncoder()
        self.quantum_encoder = QuantumBitEncoder()
        self.encoding_history: List[QBCState] = []

    def encode(self, classical_bit: int, noise_samples: int = 256) -> QBCState:
        """
        Full QBC encoding pipeline:
        Classical bit → Noise pattern → Quantum state
        """
        # Step 1: Encode to noise
        noise_pattern = self.noise_encoder.encode_bit(classical_bit, noise_samples)

        # Step 2: Convert to quantum
        alpha, beta = self.quantum_encoder.bit_to_quantum(classical_bit, noise_pattern)

        # Step 3: Calculate coherence quality
        noise_variance = np.var(noise_pattern) if noise_pattern else 0.0
        coherence = min(1.0, max(0.0, 1.0 - noise_variance / 10000.0))

        state = QBCState(
            quantum_amplitude_alpha=alpha,
            quantum_amplitude_beta=beta,
            classical_bit=classical_bit,
            noise_signature=noise_pattern,
            coherence_quality=coherence,
            timestamp_ns=time.perf_counter_ns()
        )

        self.encoding_history.append(state)
        return state

    def decode(self, state: QBCState) -> int:
        """
        Full QBC decoding pipeline:
        Quantum state → Classical bit
        """
        return self.quantum_encoder.quantum_to_bit(
            state.quantum_amplitude_alpha,
            state.quantum_amplitude_beta
        )

    def encode_byte(self, byte_val: int) -> List[QBCState]:
        """Encode an 8-bit byte as 8 QBC states"""
        states = []
        for i in range(8):
            bit = (byte_val >> i) & 1
            state = self.encode(bit, noise_samples=32)
            states.append(state)
        return states

    def decode_byte(self, states: List[QBCState]) -> int:
        """Decode 8 QBC states back to byte"""
        byte_val = 0
        for i, state in enumerate(states[:8]):
            bit = self.decode(state)
            byte_val |= (bit << i)
        return byte_val

    def encode_string(self, text: str) -> List[QBCState]:
        """Encode a string as QBC states"""
        all_states = []
        for char in text:
            byte_val = ord(char)
            states = self.encode_byte(byte_val)
            all_states.extend(states)
        return all_states

    def decode_string(self, states: List[QBCState]) -> str:
        """Decode QBC states back to string"""
        text = ""
        for i in range(0, len(states), 8):
            byte_states = states[i:i+8]
            if len(byte_states) == 8:
                byte_val = self.decode_byte(byte_states)
                text += chr(byte_val)
        return text

    def get_statistics(self) -> Dict[str, float]:
        """Get encoding statistics"""
        if not self.encoding_history:
            return {}

        coherences = [s.coherence_quality for s in self.encoding_history]

        return {
            'total_encodings': len(self.encoding_history),
            'avg_coherence': sum(coherences) / len(coherences),
            'min_coherence': min(coherences),
            'max_coherence': max(coherences),
            'success_rate': sum(1 for c in coherences if c > 0.5) / len(coherences)
        }


def test_qbc_encoding():
    """Test the QBC encoding system"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║           QBC ENCODING SYSTEM TEST                               ║")
    print("║           Quantum-Bit-Classical Translation                      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    encoder = QBCEncoder()

    # Test 1: Single bit encoding
    print("TEST 1: Single Bit Encoding")
    print("-" * 70)
    for bit in [0, 1]:
        state = encoder.encode(bit)
        decoded = encoder.decode(state)
        print(f"   Bit {bit}:")
        print(f"      α = {state.quantum_amplitude_alpha:.4f}")
        print(f"      β = {state.quantum_amplitude_beta:.4f}")
        print(f"      Decoded: {decoded}")
        print(f"      Coherence: {state.coherence_quality:.4f}")
        print(f"      Match: {'✓' if decoded == bit else '✗'}")
        print()

    # Test 2: Byte encoding
    print("TEST 2: Byte Encoding")
    print("-" * 70)
    test_byte = 0xA5  # 10100101
    states = encoder.encode_byte(test_byte)
    decoded_byte = encoder.decode_byte(states)
    print(f"   Original byte: 0x{test_byte:02X} ({test_byte:08b})")
    print(f"   Decoded byte:  0x{decoded_byte:02X} ({decoded_byte:08b})")
    print(f"   Match: {'✓' if decoded_byte == test_byte else '✗'}")
    print()

    # Test 3: String encoding
    print("TEST 3: String Encoding")
    print("-" * 70)
    test_string = "OAGI"
    states = encoder.encode_string(test_string)
    decoded_string = encoder.decode_string(states)
    print(f"   Original: '{test_string}'")
    print(f"   QBC states: {len(states)}")
    print(f"   Decoded: '{decoded_string}'")
    print(f"   Match: {'✓' if decoded_string == test_string else '✗'}")
    print()

    # Test 4: Statistics
    print("TEST 4: Encoding Statistics")
    print("-" * 70)
    stats = encoder.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value:.4f}")
    print()

    print("✅ QBC ENCODING SYSTEM TEST COMPLETE")


if __name__ == "__main__":
    test_qbc_encoding()
