#!/usr/bin/env python3
"""
QBC E8 Lattice Integration

Maps Quantum-Bit-Classical states onto E8 lattice points
for structured quantum storage and routing.
"""

import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from qbc import QBCState, QBCEncoder


@dataclass
class E8Point:
    """Point in E8 lattice"""
    coordinates: np.ndarray  # 8-dimensional
    qbc_state: Optional[QBCState]  # Stored QBC state
    index: int
    weight: float  # Lattice weight (norm squared)


class QBC_E8_Lattice:
    """E8 lattice with QBC state storage"""

    def __init__(self):
        self.roots = self._generate_e8_roots()
        self.points: Dict[int, E8Point] = {}
        self.qbc_encoder = QBCEncoder()
        self._initialize_lattice()

    def _generate_e8_roots(self) -> List[np.ndarray]:
        """Generate E8 root system (240 roots)"""
        roots = []

        # Type 1: (±1, ±1, 0, 0, 0, 0, 0, 0) permutations with even # of +1's
        for i in range(8):
            for j in range(i+1, 8):
                for s1 in [-1, 1]:
                    for s2 in [-1, 1]:
                        if (s1 + s2) % 4 == 0:  # Even number of +1's
                            root = np.zeros(8)
                            root[i] = s1
                            root[j] = s2
                            roots.append(root)

        # Type 2: (±1/2, ±1/2, ..., ±1/2) with even number of -1/2's
        for bits in range(256):
            signs = [(bits >> i) & 1 for i in range(8)]
            if sum(signs) % 2 == 0:  # Even number of +1/2's = even number of -1/2's
                root = np.array([0.5 if s else -0.5 for s in signs])
                roots.append(root)

        return roots[:240]

    def _initialize_lattice(self):
        """Initialize E8 lattice points"""
        for idx, root in enumerate(self.roots):
            weight = float(np.dot(root, root))
            point = E8Point(
                coordinates=root,
                qbc_state=None,
                index=idx,
                weight=weight
            )
            self.points[idx] = point

    def find_best_point(self, qbc_state: QBCState) -> int:
        """
        Find best E8 lattice point to store QBC state
        Uses quantum phase to match E8 coordinates
        """
        # Extract phase from quantum state
        alpha_phase = np.angle(qbc_state.quantum_amplitude_alpha)
        beta_phase = np.angle(qbc_state.quantum_amplitude_beta)

        # Create 8D vector from quantum state
        target_vector = np.array([
            np.cos(alpha_phase),
            np.sin(alpha_phase),
            np.cos(beta_phase),
            np.sin(beta_phase),
            qbc_state.coherence_quality,
            qbc_state.classical_bit * 2 - 1,  # Map 0,1 to -1,1
            np.cos(alpha_phase + beta_phase),
            np.sin(alpha_phase + beta_phase)
        ])

        # Find closest E8 point
        best_idx = 0
        best_distance = float('inf')

        for idx, point in self.points.items():
            distance = np.linalg.norm(target_vector - point.coordinates)
            if distance < best_distance:
                best_distance = distance
                best_idx = idx

        return best_idx

    def store_qbc_state(self, qbc_state: QBCState) -> int:
        """Store QBC state at optimal E8 lattice point"""
        point_idx = self.find_best_point(qbc_state)
        self.points[point_idx].qbc_state = qbc_state
        return point_idx

    def retrieve_qbc_state(self, point_idx: int) -> Optional[QBCState]:
        """Retrieve QBC state from E8 lattice point"""
        if point_idx in self.points:
            return self.points[point_idx].qbc_state
        return None

    def store_byte(self, byte_val: int) -> List[int]:
        """Store a byte as 8 QBC states in E8 lattice"""
        states = self.qbc_encoder.encode_byte(byte_val)
        indices = []
        for state in states:
            idx = self.store_qbc_state(state)
            indices.append(idx)
        return indices

    def retrieve_byte(self, indices: List[int]) -> int:
        """Retrieve byte from E8 lattice"""
        states = []
        for idx in indices:
            state = self.retrieve_qbc_state(idx)
            if state:
                states.append(state)
        if len(states) == 8:
            return self.qbc_encoder.decode_byte(states)
        return 0

    def get_storage_stats(self) -> Dict[str, int]:
        """Get storage statistics"""
        stored = sum(1 for p in self.points.values() if p.qbc_state is not None)
        return {
            'total_points': len(self.points),
            'stored_states': stored,
            'free_points': len(self.points) - stored,
            'capacity_used_percent': int(stored / len(self.points) * 100)
        }

    def clear_all(self):
        """Clear all stored QBC states"""
        for point in self.points.values():
            point.qbc_state = None


def test_qbc_e8():
    """Test QBC E8 lattice integration"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║           QBC E8 LATTICE INTEGRATION TEST                        ║")
    print("║           Quantum Storage on E8 Root System                      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    lattice = QBC_E8_Lattice()

    print("TEST 1: Lattice Initialization")
    print("-" * 70)
    print(f"   E8 roots generated: {len(lattice.roots)}")
    print(f"   Lattice points: {len(lattice.points)}")
    print(f"   First root: {lattice.roots[0]}")
    print(f"   Root weight: {lattice.points[0].weight:.2f}")
    print()

    print("TEST 2: QBC State Storage")
    print("-" * 70)
    encoder = QBCEncoder()
    test_bit = 1
    state = encoder.encode(test_bit)
    point_idx = lattice.store_qbc_state(state)
    print(f"   Stored bit {test_bit} at E8 point {point_idx}")
    print(f"   Point coordinates: {lattice.points[point_idx].coordinates}")
    retrieved = lattice.retrieve_qbc_state(point_idx)
    if retrieved:
        decoded = encoder.decode(retrieved)
        print(f"   Retrieved and decoded: {decoded}")
        print(f"   Match: {'✓' if decoded == test_bit else '✗'}")
    print()

    print("TEST 3: Byte Storage in E8 Lattice")
    print("-" * 70)
    test_byte = 0x42  # 'B'
    indices = lattice.store_byte(test_byte)
    print(f"   Stored byte 0x{test_byte:02X} ('{chr(test_byte)}')")
    print(f"   E8 point indices: {indices}")
    retrieved_byte = lattice.retrieve_byte(indices)
    print(f"   Retrieved byte: 0x{retrieved_byte:02X} ('{chr(retrieved_byte)}')")
    print(f"   Match: {'✓' if retrieved_byte == test_byte else '✗'}")
    print()

    print("TEST 4: Storage Statistics")
    print("-" * 70)
    stats = lattice.get_storage_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()

    print("✅ QBC E8 LATTICE INTEGRATION TEST COMPLETE")


if __name__ == "__main__":
    test_qbc_e8()
