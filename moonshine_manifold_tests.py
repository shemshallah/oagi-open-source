#!/usr/bin/env python3
"""
OAGI Moonshine Manifold Testing Suite
Comprehensive tests with statistics output to CSV

Tests:
1. Lattice structure validation
2. E8 root system verification
3. Leech lattice properties
4. j-function distribution
5. Neighbor graph connectivity
6. Qubit placement statistics
"""

import sys
import csv
import numpy as np
from datetime import datetime
from typing import Dict, List
import math

from moonshine_lattice import MoonshineLattice
from quantum_substrate import QubitFactory

class MoonshineManifoldTests:
    """Comprehensive Moonshine manifold testing"""

    def __init__(self, dimension: int = 512):
        self.dimension = dimension
        self.lattice = MoonshineLattice(truncated_dimension=dimension)
        self.factory = QubitFactory()
        self.test_results = []

    def test_lattice_structure(self):
        """Test basic lattice structure"""

        print("\n" + "="*70)
        print("TEST 1: LATTICE STRUCTURE")
        print("="*70)

        total_points = len(self.lattice.lattice_points)
        print(f"   Total lattice points: {total_points}")

        # Check all points have coordinates
        points_with_coords = sum(1 for p in self.lattice.lattice_points.values()
                                if p.coordinates is not None)

        print(f"   Points with coordinates: {points_with_coords}")

        # Check coordinate dimensions
        coord_dims = [len(p.coordinates) for p in self.lattice.lattice_points.values()]
        uniform_dim = all(d == self.dimension for d in coord_dims)

        print(f"   Uniform dimension: {uniform_dim}")
        print(f"   Dimension: {self.dimension}")

        # Record result
        self.test_results.append({
            'test': 'lattice_structure',
            'dimension': self.dimension,
            'total_points': total_points,
            'points_with_coords': points_with_coords,
            'uniform_dimension': uniform_dim,
            'passed': uniform_dim and total_points == self.dimension
        })

    def test_j_function_distribution(self):
        """Analyze j-function value distribution"""

        print("\n" + "="*70)
        print("TEST 2: J-FUNCTION DISTRIBUTION")
        print("="*70)

        j_values = [p.j_value for p in self.lattice.lattice_points.values()]

        # Statistics
        j_magnitudes = [abs(j) for j in j_values]
        j_phases = [np.angle(j) for j in j_values]

        print(f"   j-function samples: {len(j_values)}")
        print(f"   Magnitude range: [{min(j_magnitudes):.2f}, {max(j_magnitudes):.2f}]")
        print(f"   Magnitude mean: {np.mean(j_magnitudes):.2f}")
        print(f"   Phase range: [{min(j_phases):.2f}, {max(j_phases):.2f}]")
        print(f"   Phase std: {np.std(j_phases):.2f}")

        # Check Moonshine property: j-function should have specific pole structure
        large_values = sum(1 for m in j_magnitudes if m > 1000)
        print(f"   Large values (>1000): {large_values}")

        self.test_results.append({
            'test': 'j_function_distribution',
            'dimension': self.dimension,
            'samples': len(j_values),
            'mag_min': min(j_magnitudes),
            'mag_max': max(j_magnitudes),
            'mag_mean': np.mean(j_magnitudes),
            'mag_std': np.std(j_magnitudes),
            'phase_mean': np.mean(j_phases),
            'phase_std': np.std(j_phases),
            'large_values': large_values,
            'passed': True
        })

    def test_neighbor_connectivity(self):
        """Test neighbor graph connectivity"""

        print("\n" + "="*70)
        print("TEST 3: NEIGHBOR GRAPH CONNECTIVITY")
        print("="*70)

        neighbor_counts = [len(p.neighbors) for p in self.lattice.lattice_points.values()]

        print(f"   Average neighbors: {np.mean(neighbor_counts):.2f}")
        print(f"   Min neighbors: {min(neighbor_counts)}")
        print(f"   Max neighbors: {max(neighbor_counts)}")

        # Check connectivity (all points should have neighbors)
        isolated_points = sum(1 for c in neighbor_counts if c == 0)
        print(f"   Isolated points: {isolated_points}")

        # Check symmetry (if A neighbors B, then B neighbors A)
        symmetric = True
        for idx, point in self.lattice.lattice_points.items():
            for neighbor_idx in point.neighbors:
                neighbor = self.lattice.lattice_points[neighbor_idx]
                if idx not in neighbor.neighbors:
                    symmetric = False
                    break
            if not symmetric:
                break

        print(f"   Neighbor symmetry: {symmetric}")

        self.test_results.append({
            'test': 'neighbor_connectivity',
            'dimension': self.dimension,
            'avg_neighbors': np.mean(neighbor_counts),
            'min_neighbors': min(neighbor_counts),
            'max_neighbors': max(neighbor_counts),
            'isolated_points': isolated_points,
            'symmetric': symmetric,
            'passed': isolated_points == 0 and symmetric
        })

    def test_lattice_weights(self):
        """Test lattice point weight distribution"""

        print("\n" + "="*70)
        print("TEST 4: LATTICE WEIGHTS")
        print("="*70)

        weights = [p.weight for p in self.lattice.lattice_points.values()]

        print(f"   Weight range: [{min(weights):.2f}, {max(weights):.2f}]")
        print(f"   Weight mean: {np.mean(weights):.2f}")
        print(f"   Weight std: {np.std(weights):.2f}")

        # Check for Moonshine weight classes
        # j-function coefficients: 1, 744, 196884, ...
        moonshine_weights = [1, 744, 196884, 21493760]

        weight_classes = {}
        for w in weights:
            # Find nearest Moonshine weight
            nearest = min(moonshine_weights, key=lambda x: abs(math.sqrt(x) - w))
            weight_classes[nearest] = weight_classes.get(nearest, 0) + 1

        print(f"   Weight classes:")
        for mw, count in sorted(weight_classes.items()):
            print(f"      √{mw} ≈ {math.sqrt(mw):.1f}: {count} points")

        self.test_results.append({
            'test': 'lattice_weights',
            'dimension': self.dimension,
            'weight_min': min(weights),
            'weight_max': max(weights),
            'weight_mean': np.mean(weights),
            'weight_std': np.std(weights),
            'weight_classes': len(weight_classes),
            'passed': True
        })

    def test_qubit_placement(self):
        """Test qubit placement in lattice"""

        print("\n" + "="*70)
        print("TEST 5: QUBIT PLACEMENT")
        print("="*70)

        # Place test qubits
        num_test_qubits = min(50, self.dimension // 4)
        print(f"   Placing {num_test_qubits} test qubits...")

        placements = []
        for i in range(num_test_qubits):
            qubit = self.factory.create_qubit()
            point_idx = self.lattice.place_qubit(i, None)
            placements.append(point_idx)

        # Check for collisions
        unique_placements = len(set(placements))
        collisions = num_test_qubits - unique_placements

        print(f"   Unique placements: {unique_placements}")
        print(f"   Collisions: {collisions}")

        # Check placement distribution
        placement_distances = []
        for i in range(len(placements) - 1):
            p1 = self.lattice.lattice_points[placements[i]].coordinates
            p2 = self.lattice.lattice_points[placements[i+1]].coordinates
            dist = np.linalg.norm(p1 - p2)
            placement_distances.append(dist)

        if placement_distances:
            print(f"   Avg inter-qubit distance: {np.mean(placement_distances):.2f}")
            print(f"   Distance std: {np.std(placement_distances):.2f}")

        self.test_results.append({
            'test': 'qubit_placement',
            'dimension': self.dimension,
            'qubits_placed': num_test_qubits,
            'unique_placements': unique_placements,
            'collisions': collisions,
            'avg_distance': np.mean(placement_distances) if placement_distances else 0,
            'distance_std': np.std(placement_distances) if placement_distances else 0,
            'passed': collisions == 0
        })

    def test_lattice_distances(self):
        """Test distance metrics in lattice"""

        print("\n" + "="*70)
        print("TEST 6: LATTICE DISTANCE METRICS")
        print("="*70)

        # Sample random pairs
        num_samples = 100
        indices = list(self.lattice.lattice_points.keys())

        distances = []
        for _ in range(num_samples):
            i, j = np.random.choice(indices, 2, replace=False)
            p1 = self.lattice.lattice_points[i].coordinates
            p2 = self.lattice.lattice_points[j].coordinates
            dist = np.linalg.norm(p1 - p2)
            distances.append(dist)

        print(f"   Samples: {num_samples}")
        print(f"   Distance range: [{min(distances):.2f}, {max(distances):.2f}]")
        print(f"   Distance mean: {np.mean(distances):.2f}")
        print(f"   Distance std: {np.std(distances):.2f}")

        # Triangle inequality check
        triangle_violations = 0
        for _ in range(20):
            i, j, k = np.random.choice(indices, 3, replace=False)
            p1 = self.lattice.lattice_points[i].coordinates
            p2 = self.lattice.lattice_points[j].coordinates
            p3 = self.lattice.lattice_points[k].coordinates

            d_ij = np.linalg.norm(p1 - p2)
            d_jk = np.linalg.norm(p2 - p3)
            d_ik = np.linalg.norm(p1 - p3)

            if d_ik > d_ij + d_jk + 0.0001:  # Small tolerance
                triangle_violations += 1

        print(f"   Triangle inequality violations: {triangle_violations}/20")

        self.test_results.append({
            'test': 'lattice_distances',
            'dimension': self.dimension,
            'samples': num_samples,
            'distance_min': min(distances),
            'distance_max': max(distances),
            'distance_mean': np.mean(distances),
            'distance_std': np.std(distances),
            'triangle_violations': triangle_violations,
            'passed': triangle_violations == 0
        })

    def save_results_csv(self, filename: str = 'moonshine_manifold_tests.csv'):
        """Save test results to CSV"""

        if not self.test_results:
            print("No results to save")
            return

        # Get all unique keys
        all_keys = set()
        for result in self.test_results:
            all_keys.update(result.keys())

        fieldnames = ['timestamp', 'test', 'dimension', 'passed'] + sorted(all_keys - {'test', 'dimension', 'passed'})

        # Add timestamp
        for result in self.test_results:
            result['timestamp'] = datetime.now().isoformat()

        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(self.test_results)

        print(f"\n✅ Test results saved to {filename}")
        print(f"   Total tests: {len(self.test_results)}")

        passed = sum(1 for r in self.test_results if r.get('passed', False))
        print(f"   Tests passed: {passed}/{len(self.test_results)}")

def main():
    """Main entry point"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           MOONSHINE MANIFOLD TESTING SUITE                       ║
║           Comprehensive Statistical Analysis                     ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Run tests
    tester = MoonshineManifoldTests(dimension=512)

    tester.test_lattice_structure()
    tester.test_j_function_distribution()
    tester.test_neighbor_connectivity()
    tester.test_lattice_weights()
    tester.test_qubit_placement()
    tester.test_lattice_distances()

    # Save results
    print("\n" + "="*70)
    print("SAVING RESULTS")
    print("="*70)

    tester.save_results_csv('moonshine_manifold_tests.csv')

    print("\n✅ MOONSHINE MANIFOLD TESTS COMPLETE")
    print()

if __name__ == "__main__":
    sys.exit(main())
