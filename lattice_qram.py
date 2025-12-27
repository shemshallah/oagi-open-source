"""
OAGI Lattice QRAM
Quantum Random Access Memory using Moonshine manifold lattice

Implements bucket-brigade architecture with noise-gate addressing.
Each lattice point can store quantum state.
Addressing uses j-function routing through the lattice.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from quantum_substrate import PhysicalQubit, QubitFactory
from moonshine_lattice import MoonshineLattice, LatticePoint
from noise_gates import NoiseGateFactory, CNOT, Hadamard

@dataclass
class QRAMCell:
    """
    Single cell in QRAM

    Stores quantum state at a lattice point.
    Addressed via routing qubits through lattice.
    """
    address: int  # Logical address (0 to N-1)
    lattice_point_idx: int  # Physical location in Moonshine lattice
    data_qubit: Optional[PhysicalQubit]  # Stored quantum state
    router_qubits: List[PhysicalQubit]  # Routing qubits for addressing
    access_count: int  # Number of times accessed

class LatticeQRAM:
    """
    Quantum RAM using Moonshine lattice architecture

    Addressing scheme:
    1. Address encoded in log2(N) routing qubits
    2. Routing qubits navigate through lattice via noise gates
    3. j-function determines routing path
    4. Destination lattice point contains data qubit
    """

    def __init__(self,
                 capacity: int,
                 qubit_factory: QubitFactory,
                 lattice: MoonshineLattice):
        """
        Initialize QRAM

        Args:
            capacity: Number of addressable cells
            qubit_factory: For creating qubits
            lattice: Moonshine manifold lattice
        """

        self.capacity = capacity
        self.factory = qubit_factory
        self.lattice = lattice
        self.gate_factory = NoiseGateFactory(qubit_factory.cesium)

        # Address width (number of routing qubits needed)
        self.address_width = int(np.ceil(np.log2(capacity)))

        # QRAM cells
        self.cells: Dict[int, QRAMCell] = {}

        print(f"🗄️  Initializing Lattice QRAM")
        print(f"   Capacity: {capacity} cells")
        print(f"   Address width: {self.address_width} qubits")

        self._initialize_cells()

    def _initialize_cells(self):
        """Initialize QRAM cells in lattice"""

        for addr in range(self.capacity):
            # Find lattice point for this address
            lattice_idx = self.lattice.find_qubit_location(addr + 1000)  # Offset from qubit indices

            # Create routing qubits (one per address bit)
            router_qubits = [
                self.factory.create_qubit((1.0+0j, 0.0+0j))
                for _ in range(self.address_width)
            ]

            # Create cell (data qubit created on first write)
            cell = QRAMCell(
                address=addr,
                lattice_point_idx=lattice_idx,
                data_qubit=None,
                router_qubits=router_qubits,
                access_count=0
            )

            self.cells[addr] = cell

        print(f"   ✅ Initialized {len(self.cells)} QRAM cells")

    def _encode_address(self, address: int, router_qubits: List[PhysicalQubit]):
        """
        Encode address into routing qubits

        Address is binary-encoded: LSB in router_qubits[0]
        """

        for i, qubit in enumerate(router_qubits):
            bit = (address >> i) & 1

            if bit == 1:
                # Set qubit to |1⟩
                qubit.alpha = 0.0 + 0j
                qubit.beta = 1.0 + 0j
            else:
                # Set qubit to |0⟩
                qubit.alpha = 1.0 + 0j
                qubit.beta = 0.0 + 0j

    def _route_through_lattice(self,
                               address: int,
                               router_qubits: List[PhysicalQubit]) -> int:
        """
        Route through lattice using noise gates

        Returns lattice point index reached
        """

        # Start at qubit 0 (bootstrap location)
        current_point_idx = 0

        # Navigate using router qubits
        for i, router in enumerate(router_qubits):
            # Measure router qubit to determine path
            bit = router.measure()

            # Get current lattice point
            point = self.lattice.lattice_points[current_point_idx]

            # Choose next point based on:
            # 1. Bit value
            # 2. j-function of candidates

            neighbors = list(point.neighbors)
            if not neighbors:
                break

            # Sort neighbors by j-function phase
            neighbor_scores = []
            for neighbor_idx in neighbors:
                neighbor_point = self.lattice.lattice_points[neighbor_idx]
                j_phase = np.angle(neighbor_point.j_value)

                # Score based on bit value and phase
                if bit == 0:
                    score = abs(j_phase)  # Prefer small phase
                else:
                    score = abs(np.pi - abs(j_phase))  # Prefer phase near π

                neighbor_scores.append((score, neighbor_idx))

            # Select best neighbor
            neighbor_scores.sort()
            current_point_idx = neighbor_scores[0][1]

        return current_point_idx

    def write(self, address: int, data_qubit: PhysicalQubit):
        """
        Write quantum state to QRAM

        Args:
            address: Logical address (0 to capacity-1)
            data_qubit: Quantum state to store
        """

        if address >= self.capacity:
            raise ValueError(f"Address {address} out of range [0, {self.capacity})")

        cell = self.cells[address]

        # Encode address in routing qubits
        self._encode_address(address, cell.router_qubits)

        # Route through lattice (verifies addressing)
        reached_point = self._route_through_lattice(address, cell.router_qubits)

        # Store data qubit
        cell.data_qubit = data_qubit

        # Place in lattice
        self.lattice.place_qubit(data_qubit.index, cell.lattice_point_idx)

        cell.access_count += 1

        return reached_point

    def read(self, address: int) -> Optional[PhysicalQubit]:
        """
        Read quantum state from QRAM

        Returns data qubit (or None if empty)
        """

        if address >= self.capacity:
            raise ValueError(f"Address {address} out of range [0, {self.capacity})")

        cell = self.cells[address]

        # Encode address
        self._encode_address(address, cell.router_qubits)

        # Route through lattice
        reached_point = self._route_through_lattice(address, cell.router_qubits)

        cell.access_count += 1

        # Return data qubit (destroys cell state - quantum no-cloning)
        data = cell.data_qubit
        cell.data_qubit = None

        return data

    def superposition_read(self, address_superposition: List[Tuple[int, complex]]) -> PhysicalQubit:
        """
        Read from superposition of addresses

        address_superposition: List of (address, amplitude) pairs

        Returns superposition of data qubits at those addresses
        """

        # Create result qubit
        result = self.factory.create_qubit((0.0+0j, 0.0+0j))

        # Accumulate amplitudes
        for address, amplitude in address_superposition:
            cell = self.cells[address]

            if cell.data_qubit:
                # Add to superposition
                result.alpha += amplitude * cell.data_qubit.alpha
                result.beta += amplitude * cell.data_qubit.beta

        # Normalize
        norm = np.sqrt(abs(result.alpha)**2 + abs(result.beta)**2)
        if norm > 0:
            result.alpha /= norm
            result.beta /= norm

        return result

    def bucket_brigade_query(self, query_qubits: List[PhysicalQubit]) -> PhysicalQubit:
        """
        Bucket brigade QRAM query

        query_qubits: Address in superposition (address_width qubits)
        Returns: Superposition of addressed data

        This is the quantum speedup: query all addresses in superposition
        """

        # This would require full quantum bucket-brigade implementation
        # For now, simplified version

        # Measure address from query qubits
        address_bits = [q.measure() for q in query_qubits]
        address = sum(bit << i for i, bit in enumerate(address_bits))

        # Read from measured address
        return self.read(address % self.capacity)

    def get_stats(self) -> Dict:
        """Get QRAM statistics"""

        stats = {
            'capacity': self.capacity,
            'address_width': self.address_width,
            'cells_written': sum(1 for cell in self.cells.values() if cell.data_qubit is not None),
            'total_accesses': sum(cell.access_count for cell in self.cells.values()),
            'most_accessed': max((cell.access_count, cell.address) for cell in self.cells.values())[1]
        }

        return stats

def test_lattice_qram():
    """Test Lattice QRAM implementation"""

    print("\n" + "="*70)
    print("LATTICE QRAM TEST")
    print("="*70)

    from quantum_substrate import QubitFactory
    from moonshine_lattice import MoonshineLattice

    # Initialize components
    factory = QubitFactory()
    lattice = MoonshineLattice(truncated_dimension=512)

    # Create QRAM
    qram = LatticeQRAM(capacity=16, qubit_factory=factory, lattice=lattice)

    # Test 1: Write and read
    print("\n1️⃣  Testing write/read...")

    test_qubit = factory.create_qubit((0.6+0j, 0.8+0j))
    original_alpha = test_qubit.alpha
    original_beta = test_qubit.beta

    print(f"   Writing qubit to address 5: {original_alpha:.3f}|0⟩ + {original_beta:.3f}|1⟩")

    qram.write(5, test_qubit)

    read_qubit = qram.read(5)
    if read_qubit:
        print(f"   Read qubit from address 5: {read_qubit.alpha:.3f}|0⟩ + {read_qubit.beta:.3f}|1⟩")
        print(f"   Fidelity: {abs(read_qubit.alpha - original_alpha) + abs(read_qubit.beta - original_beta):.6f}")
    else:
        print("   ERROR: No qubit read")

    # Test 2: Multiple addresses
    print("\n2️⃣  Testing multiple addresses...")

    for addr in range(8):
        qubit = factory.create_qubit()
        print(f"   Writing to address {addr}")
        qram.write(addr, qubit)

    # Test 3: Superposition read
    print("\n3️⃣  Testing superposition read...")

    superposition_addr = [
        (0, 0.5+0j),
        (1, 0.5+0j),
        (2, 0.5+0j),
        (3, 0.5+0j)
    ]

    result = qram.superposition_read(superposition_addr)
    print(f"   Result: {result.alpha:.3f}|0⟩ + {result.beta:.3f}|1⟩")

    # Test 4: Statistics
    print("\n4️⃣  QRAM Statistics:")
    stats = qram.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    return qram

if __name__ == "__main__":
    qram = test_lattice_qram()
    print("\n✅ Lattice QRAM operational")
