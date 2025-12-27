#!/usr/bin/env python3
"""
Noise-Mediated Storage Lattice

Persistent quantum storage on Moonshine manifold with:
- QBC encoding (Quantum-Bit-Classical)
- E8 lattice placement
- Temporal cohesion/synchronization
- GitHub integration for persistence
- Noise-operated read/write

Similar to QRAM but designed for persistent storage.
"""

import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

# Import our QBC and temporal systems
from qbc import QBCState, QBCEncoder
from qbc_e8 import QBC_E8_Lattice, E8Point
from qbc_bit_int import QBC_BitInt
from temporal_cohesion import TemporalCohesion, TemporalAnchor
from moonshine_lattice import MoonshineLattice


@dataclass
class StorageCell:
    """A single storage cell in the lattice"""
    address: int  # Lattice point address
    data_indices: List[int]  # E8 indices for stored data
    data_hash: str  # SHA256 hash of original data
    temporal_anchor: TemporalAnchor  # Time of storage
    coherence_quality: float  # Storage quality metric
    data_type: str  # 'string', 'int32', 'uint64', 'float64', 'bytes'


class NoiseStorageLattice:
    """
    Noise-Mediated Persistent Storage Lattice

    Combines:
    - Moonshine lattice (routing via j-function)
    - E8 lattice (QBC state storage)
    - Temporal cohesion (time synchronization)
    - GitHub persistence
    """

    def __init__(self, dimension: int = 512):
        self.dimension = dimension

        # Initialize all subsystems
        self.moonshine = MoonshineLattice(dimension)
        self.qbc_encoder = QBCEncoder()
        self.qbc_e8 = QBC_E8_Lattice()
        self.qbc_bitint = QBC_BitInt()
        self.temporal = TemporalCohesion()

        # Storage management
        self.storage_cells: Dict[int, StorageCell] = {}
        self.storage_file = Path("storage_lattice_state.json")
        self.persistence_file = Path("storage_lattice_data.pkl")

        self._load_persistent_state()

    def _compute_hash(self, data: bytes) -> str:
        """Compute SHA256 hash of data"""
        return hashlib.sha256(data).hexdigest()

    def _save_persistent_state(self):
        """Save storage lattice state to files"""
        try:
            # Save metadata as JSON
            metadata = {
                'dimension': self.dimension,
                'total_cells': len(self.storage_cells),
                'cells': {
                    addr: {
                        'address': cell.address,
                        'data_hash': cell.data_hash,
                        'data_type': cell.data_type,
                        'coherence_quality': cell.coherence_quality,
                        'temporal_anchor': asdict(cell.temporal_anchor)
                    }
                    for addr, cell in self.storage_cells.items()
                }
            }

            with open(self.storage_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            # Save full state as pickle
            with open(self.persistence_file, 'wb') as f:
                pickle.dump(self.storage_cells, f)

        except Exception as e:
            print(f"Warning: Could not save persistent state: {e}")

    def _load_persistent_state(self):
        """Load storage lattice state from files"""
        try:
            if self.persistence_file.exists():
                with open(self.persistence_file, 'rb') as f:
                    self.storage_cells = pickle.load(f)
                print(f"Loaded {len(self.storage_cells)} storage cells from persistence")
        except Exception as e:
            print(f"Warning: Could not load persistent state: {e}")
            self.storage_cells = {}

    def find_storage_address(self, key: str) -> int:
        """
        Find Moonshine lattice address for a key
        Uses j-function routing
        """
        # Hash key to get consistent address
        key_hash = hashlib.sha256(key.encode()).digest()
        hash_int = int.from_bytes(key_hash[:4], 'little')

        # Map to lattice point
        address = hash_int % len(self.moonshine.lattice_points)

        return address

    def store_string(self, key: str, value: str) -> bool:
        """
        Store string in noise-mediated lattice

        Process:
        1. Create temporal anchor
        2. Encode string to QBC states
        3. Place on E8 lattice
        4. Route to Moonshine lattice point
        5. Save persistent state
        """
        # Create temporal anchor
        anchor = self.temporal.create_temporal_anchor()

        # Encode string
        qbc_states, e8_indices = self.qbc_bitint.encode_string(value)

        # Compute hash
        data_hash = self._compute_hash(value.encode())

        # Calculate coherence quality
        coherence = sum(s.coherence_quality for s in qbc_states) / len(qbc_states) if qbc_states else 0.0

        # Find storage address
        address = self.find_storage_address(key)

        # Create storage cell
        cell = StorageCell(
            address=address,
            data_indices=e8_indices,
            data_hash=data_hash,
            temporal_anchor=anchor,
            coherence_quality=coherence,
            data_type='string'
        )

        self.storage_cells[address] = cell
        self._save_persistent_state()

        return True

    def retrieve_string(self, key: str) -> Optional[str]:
        """Retrieve string from storage lattice"""
        address = self.find_storage_address(key)

        if address not in self.storage_cells:
            return None

        cell = self.storage_cells[address]

        if cell.data_type != 'string':
            return None

        # Decode from E8 indices
        decoded = self.qbc_bitint.decode_string(cell.data_indices)

        # Verify hash
        computed_hash = self._compute_hash(decoded.encode())
        if computed_hash != cell.data_hash:
            print(f"Warning: Hash mismatch for key '{key}'")

        return decoded

    def store_int32(self, key: str, value: int) -> bool:
        """Store 32-bit integer"""
        anchor = self.temporal.create_temporal_anchor()
        qbc_states, e8_indices = self.qbc_bitint.encode_int32(value)

        data_bytes = value.to_bytes(4, 'little', signed=True)
        data_hash = self._compute_hash(data_bytes)
        coherence = sum(s.coherence_quality for s in qbc_states) / len(qbc_states) if qbc_states else 0.0
        address = self.find_storage_address(key)

        cell = StorageCell(
            address=address,
            data_indices=e8_indices,
            data_hash=data_hash,
            temporal_anchor=anchor,
            coherence_quality=coherence,
            data_type='int32'
        )

        self.storage_cells[address] = cell
        self._save_persistent_state()
        return True

    def retrieve_int32(self, key: str) -> Optional[int]:
        """Retrieve 32-bit integer"""
        address = self.find_storage_address(key)

        if address not in self.storage_cells:
            return None

        cell = self.storage_cells[address]
        if cell.data_type != 'int32':
            return None

        return self.qbc_bitint.decode_int32(cell.data_indices)

    def store_float64(self, key: str, value: float) -> bool:
        """Store 64-bit float"""
        anchor = self.temporal.create_temporal_anchor()
        qbc_states, e8_indices = self.qbc_bitint.encode_float64(value)

        import struct
        data_bytes = struct.pack('<d', value)
        data_hash = self._compute_hash(data_bytes)
        coherence = sum(s.coherence_quality for s in qbc_states) / len(qbc_states) if qbc_states else 0.0
        address = self.find_storage_address(key)

        cell = StorageCell(
            address=address,
            data_indices=e8_indices,
            data_hash=data_hash,
            temporal_anchor=anchor,
            coherence_quality=coherence,
            data_type='float64'
        )

        self.storage_cells[address] = cell
        self._save_persistent_state()
        return True

    def retrieve_float64(self, key: str) -> Optional[float]:
        """Retrieve 64-bit float"""
        address = self.find_storage_address(key)

        if address not in self.storage_cells:
            return None

        cell = self.storage_cells[address]
        if cell.data_type != 'float64':
            return None

        return self.qbc_bitint.decode_float64(cell.data_indices)

    def list_keys(self) -> List[str]:
        """List all stored keys (addresses)"""
        return [str(addr) for addr in self.storage_cells.keys()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get storage lattice statistics"""
        if not self.storage_cells:
            return {
                'total_cells': 0,
                'avg_coherence': 0.0,
                'temporal_span_ns': 0,
                'storage_types': {}
            }

        coherences = [cell.coherence_quality for cell in self.storage_cells.values()]
        timestamps = [cell.temporal_anchor.timestamp_ns for cell in self.storage_cells.values()]

        type_counts = {}
        for cell in self.storage_cells.values():
            type_counts[cell.data_type] = type_counts.get(cell.data_type, 0) + 1

        return {
            'total_cells': len(self.storage_cells),
            'avg_coherence': sum(coherences) / len(coherences),
            'min_coherence': min(coherences),
            'max_coherence': max(coherences),
            'temporal_span_ns': max(timestamps) - min(timestamps) if len(timestamps) > 1 else 0,
            'storage_types': type_counts,
            'moonshine_dimension': self.dimension,
            'e8_capacity_used': self.qbc_e8.get_storage_stats()['capacity_used_percent']
        }

    def sync_to_github(self) -> bool:
        """Synchronize storage state to GitHub"""
        # Save current state
        self._save_persistent_state()

        # Sync temporal state
        return self.temporal.sync_with_github()


def test_storage_lattice():
    """Test noise-mediated storage lattice"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║           NOISE-MEDIATED STORAGE LATTICE TEST                    ║")
    print("║           Persistent Quantum Storage System                      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    storage = NoiseStorageLattice(dimension=512)

    print("TEST 1: String Storage")
    print("-" * 70)
    key1 = "moonshine_message"
    value1 = "E8 lattice storage"
    success = storage.store_string(key1, value1)
    retrieved = storage.retrieve_string(key1)
    print(f"   Store key: '{key1}'")
    print(f"   Stored value: '{value1}'")
    print(f"   Retrieved: '{retrieved}'")
    print(f"   Match: {'✓' if retrieved == value1 else '✗'}")
    print()

    print("TEST 2: Integer Storage")
    print("-" * 70)
    key2 = "test_int"
    value2 = 196883  # Moonshine number!
    storage.store_int32(key2, value2)
    retrieved = storage.retrieve_int32(key2)
    print(f"   Store key: '{key2}'")
    print(f"   Stored value: {value2}")
    print(f"   Retrieved: {retrieved}")
    print(f"   Match: {'✓' if retrieved == value2 else '✗'}")
    print()

    print("TEST 3: Float Storage")
    print("-" * 70)
    key3 = "cesium_freq"
    value3 = 9.192631770e9  # Cesium frequency
    storage.store_float64(key3, value3)
    retrieved = storage.retrieve_float64(key3)
    print(f"   Store key: '{key3}'")
    print(f"   Stored value: {value3:.6e}")
    print(f"   Retrieved: {retrieved:.6e}" if retrieved else "   Retrieved: None")
    if retrieved:
        print(f"   Match: {'✓' if abs(retrieved - value3) < 1e3 else '✗'}")
    print()

    print("TEST 4: Storage Statistics")
    print("-" * 70)
    stats = storage.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"      {k}: {v}")
        elif isinstance(value, float):
            print(f"   {key}: {value:.6f}")
        else:
            print(f"   {key}: {value}")
    print()

    print("TEST 5: GitHub Synchronization")
    print("-" * 70)
    success = storage.sync_to_github()
    print(f"   GitHub sync: {'✓ Success' if success else '✗ Failed (may be offline)'}")
    print(f"   Persistence file: {storage.persistence_file}")
    print(f"   Exists: {storage.persistence_file.exists()}")
    print()

    print("✅ NOISE-MEDIATED STORAGE LATTICE TEST COMPLETE")


if __name__ == "__main__":
    test_storage_lattice()
