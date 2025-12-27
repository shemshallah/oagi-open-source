#!/usr/bin/env python3
"""
QBC Bit-Int Conversion Module

High-level encoding/decoding of integers, floats, and complex data types
using QBC (Quantum-Bit-Classical) encoding on E8 lattice.
"""

import struct
import numpy as np
from typing import List, Tuple, Dict, Any
from qbc import QBCState, QBCEncoder
from qbc_e8 import QBC_E8_Lattice


class QBC_BitInt:
    """Quantum-Bit-Classical integer and data type conversions"""

    def __init__(self):
        self.encoder = QBCEncoder()
        self.e8_lattice = QBC_E8_Lattice()

    def encode_int32(self, value: int) -> Tuple[List[QBCState], List[int]]:
        """
        Encode 32-bit signed integer to QBC states and E8 lattice points
        Returns: (qbc_states, e8_indices)
        """
        # Pack as 32-bit integer
        packed = struct.pack('<i', value)

        qbc_states = []
        e8_indices = []

        for byte in packed:
            byte_states = self.encoder.encode_byte(byte)
            qbc_states.extend(byte_states)

            for state in byte_states:
                idx = self.e8_lattice.store_qbc_state(state)
                e8_indices.append(idx)

        return qbc_states, e8_indices

    def decode_int32(self, e8_indices: List[int]) -> int:
        """Decode 32-bit integer from E8 lattice points"""
        if len(e8_indices) != 32:  # 4 bytes * 8 bits
            return 0

        bytes_array = bytearray()

        for i in range(0, 32, 8):
            byte_indices = e8_indices[i:i+8]
            states = [self.e8_lattice.retrieve_qbc_state(idx) for idx in byte_indices]
            states = [s for s in states if s is not None]

            if len(states) == 8:
                byte_val = self.encoder.decode_byte(states)
                bytes_array.append(byte_val)

        if len(bytes_array) == 4:
            return struct.unpack('<i', bytes(bytes_array))[0]
        return 0

    def encode_uint64(self, value: int) -> Tuple[List[QBCState], List[int]]:
        """Encode 64-bit unsigned integer"""
        packed = struct.pack('<Q', value)

        qbc_states = []
        e8_indices = []

        for byte in packed:
            byte_states = self.encoder.encode_byte(byte)
            qbc_states.extend(byte_states)

            for state in byte_states:
                idx = self.e8_lattice.store_qbc_state(state)
                e8_indices.append(idx)

        return qbc_states, e8_indices

    def decode_uint64(self, e8_indices: List[int]) -> int:
        """Decode 64-bit unsigned integer"""
        if len(e8_indices) != 64:  # 8 bytes * 8 bits
            return 0

        bytes_array = bytearray()

        for i in range(0, 64, 8):
            byte_indices = e8_indices[i:i+8]
            states = [self.e8_lattice.retrieve_qbc_state(idx) for idx in byte_indices]
            states = [s for s in states if s is not None]

            if len(states) == 8:
                byte_val = self.encoder.decode_byte(states)
                bytes_array.append(byte_val)

        if len(bytes_array) == 8:
            return struct.unpack('<Q', bytes(bytes_array))[0]
        return 0

    def encode_float64(self, value: float) -> Tuple[List[QBCState], List[int]]:
        """Encode 64-bit floating point number"""
        packed = struct.pack('<d', value)

        qbc_states = []
        e8_indices = []

        for byte in packed:
            byte_states = self.encoder.encode_byte(byte)
            qbc_states.extend(byte_states)

            for state in byte_states:
                idx = self.e8_lattice.store_qbc_state(state)
                e8_indices.append(idx)

        return qbc_states, e8_indices

    def decode_float64(self, e8_indices: List[int]) -> float:
        """Decode 64-bit floating point number"""
        if len(e8_indices) != 64:
            return 0.0

        bytes_array = bytearray()

        for i in range(0, 64, 8):
            byte_indices = e8_indices[i:i+8]
            states = [self.e8_lattice.retrieve_qbc_state(idx) for idx in byte_indices]
            states = [s for s in states if s is not None]

            if len(states) == 8:
                byte_val = self.encoder.decode_byte(states)
                bytes_array.append(byte_val)

        if len(bytes_array) == 8:
            return struct.unpack('<d', bytes(bytes_array))[0]
        return 0.0

    def encode_string(self, text: str) -> Tuple[List[QBCState], List[int]]:
        """Encode string with length prefix"""
        # Encode length as int32
        length_states, length_indices = self.encode_int32(len(text))

        qbc_states = list(length_states)
        e8_indices = list(length_indices)

        # Encode each character
        for char in text:
            byte_val = ord(char)
            byte_states = self.encoder.encode_byte(byte_val)
            qbc_states.extend(byte_states)

            for state in byte_states:
                idx = self.e8_lattice.store_qbc_state(state)
                e8_indices.append(idx)

        return qbc_states, e8_indices

    def decode_string(self, e8_indices: List[int]) -> str:
        """Decode string from E8 lattice"""
        if len(e8_indices) < 32:  # Need at least length prefix
            return ""

        # Decode length
        length = self.decode_int32(e8_indices[:32])

        if length <= 0 or length > 10000:
            return ""

        # Decode characters
        text = ""
        offset = 32

        for _ in range(length):
            if offset + 8 > len(e8_indices):
                break

            byte_indices = e8_indices[offset:offset+8]
            states = [self.e8_lattice.retrieve_qbc_state(idx) for idx in byte_indices]
            states = [s for s in states if s is not None]

            if len(states) == 8:
                byte_val = self.encoder.decode_byte(states)
                text += chr(byte_val)

            offset += 8

        return text

    def get_encoding_efficiency(self) -> Dict[str, float]:
        """Calculate encoding efficiency metrics"""
        stats = self.encoder.get_statistics()
        storage_stats = self.e8_lattice.get_storage_stats()

        return {
            'qbc_coherence': stats.get('avg_coherence', 0.0),
            'e8_capacity_used': storage_stats['capacity_used_percent'] / 100.0,
            'storage_efficiency': stats.get('success_rate', 0.0)
        }


def test_qbc_bit_int():
    """Test QBC bit-int conversions"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║           QBC BIT-INT CONVERSION TEST                            ║")
    print("║           High-Level Data Type Encoding                          ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    converter = QBC_BitInt()

    # Test 1: Int32 encoding
    print("TEST 1: Int32 Encoding")
    print("-" * 70)
    test_int = 42
    states, indices = converter.encode_int32(test_int)
    decoded_int = converter.decode_int32(indices)
    print(f"   Original: {test_int}")
    print(f"   QBC states: {len(states)}")
    print(f"   E8 indices: {len(indices)}")
    print(f"   Decoded: {decoded_int}")
    print(f"   Match: {'✓' if decoded_int == test_int else '✗'}")
    print()

    # Test 2: Uint64 encoding
    print("TEST 2: Uint64 Encoding")
    print("-" * 70)
    test_uint = 9223372036854775807  # Large number
    converter.e8_lattice.clear_all()
    states, indices = converter.encode_uint64(test_uint)
    decoded_uint = converter.decode_uint64(indices)
    print(f"   Original: {test_uint}")
    print(f"   QBC states: {len(states)}")
    print(f"   E8 indices: {len(indices)}")
    print(f"   Decoded: {decoded_uint}")
    print(f"   Match: {'✓' if decoded_uint == test_uint else '✗'}")
    print()

    # Test 3: Float64 encoding
    print("TEST 3: Float64 Encoding")
    print("-" * 70)
    test_float = 3.14159265358979
    converter.e8_lattice.clear_all()
    states, indices = converter.encode_float64(test_float)
    decoded_float = converter.decode_float64(indices)
    print(f"   Original: {test_float:.14f}")
    print(f"   QBC states: {len(states)}")
    print(f"   E8 indices: {len(indices)}")
    print(f"   Decoded: {decoded_float:.14f}")
    print(f"   Match: {'✓' if abs(decoded_float - test_float) < 1e-10 else '✗'}")
    print()

    # Test 4: String encoding
    print("TEST 4: String Encoding")
    print("-" * 70)
    test_string = "Moonshine"
    converter.e8_lattice.clear_all()
    states, indices = converter.encode_string(test_string)
    decoded_string = converter.decode_string(indices)
    print(f"   Original: '{test_string}'")
    print(f"   QBC states: {len(states)}")
    print(f"   E8 indices: {len(indices)}")
    print(f"   Decoded: '{decoded_string}'")
    print(f"   Match: {'✓' if decoded_string == test_string else '✗'}")
    print()

    # Test 5: Encoding efficiency
    print("TEST 5: Encoding Efficiency")
    print("-" * 70)
    efficiency = converter.get_encoding_efficiency()
    for key, value in efficiency.items():
        print(f"   {key}: {value:.4f}")
    print()

    print("✅ QBC BIT-INT CONVERSION TEST COMPLETE")


if __name__ == "__main__":
    test_qbc_bit_int()
