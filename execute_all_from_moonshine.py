#!/usr/bin/env python3
"""
Execute All Systems from Moonshine Terminal

Comprehensive execution script that runs all quantum systems
from the Moonshine bootstrap terminal and generates proofs.

Outputs:
- All CSV proofs to proofs/ folder
- Terminal execution logs
- System integration verification
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime


def log_section(title: str):
    """Print formatted section header"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)
    print()


def run_test_module(module_name: str, description: str) -> bool:
    """Run a Python test module and capture output"""
    print(f"Running: {description}")
    print(f"Module: {module_name}")
    print("-" * 70)

    try:
        result = subprocess.run(
            [sys.executable, module_name],
            capture_output=True,
            text=True,
            timeout=60
        )

        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0
        print(f"Status: {'✓ PASSED' if success else '✗ FAILED'}")
        print()

        return success

    except subprocess.TimeoutExpired:
        print("✗ TIMEOUT")
        print()
        return False
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print()
        return False


def main():
    """Main execution sequence"""
    start_time = datetime.now()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║        MOONSHINE QUANTUM-NOISE ARCHITECTURE                      ║")
    print("║        Complete System Execution & Proof Generation             ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print(f"Execution started: {start_time}")
    print()

    results = {}

    # Phase 1: QBC System Tests
    log_section("PHASE 1: QBC (Quantum-Bit-Classical) System")
    results['qbc'] = run_test_module('qbc.py', 'QBC Encoding System')
    results['qbc_e8'] = run_test_module('qbc_e8.py', 'QBC E8 Lattice Integration')
    results['qbc_bit_int'] = run_test_module('qbc_bit_int.py', 'QBC Bit-Int Conversions')

    # Phase 2: Temporal & Storage
    log_section("PHASE 2: Temporal Cohesion & Storage")
    results['temporal'] = run_test_module('temporal_cohesion.py', 'Temporal Synchronization')
    results['storage'] = run_test_module('storage_lattice.py', 'Noise-Mediated Storage Lattice')

    # Phase 3: Communication & Interfaces
    log_section("PHASE 3: Communication Systems")
    results['qtunnel'] = run_test_module('qtunnel.py', 'Quantum Tunnel Network')
    results['github_qc'] = run_test_module('github_qc_interface.py', 'GitHub Quantum-Classical Interface')

    # Phase 4: Quantum Algorithms
    log_section("PHASE 4: Quantum Algorithms & Proofs")
    results['shors'] = run_test_module('shors_noise_gated.py', "Shor's Factoring Algorithm")

    # Move Shor's proof to proofs folder
    shors_csv = Path("shors_quantum_advantage.csv")
    if shors_csv.exists():
        shors_csv.rename("proofs/shors_proof.csv")
        print("✓ Moved Shor's proof to proofs/shors_proof.csv")
        print()

    # Phase 5: Integration Test
    log_section("PHASE 5: Complete System Integration")
    results['integration'] = run_test_module('INTEGRATE_ALL.py', '7-Layer Quantum Stack')

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    log_section("EXECUTION SUMMARY")

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    print(f"Tests Run: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {passed / total * 100:.1f}%")
    print()
    print(f"Execution Time: {duration:.2f} seconds")
    print(f"Completed: {end_time}")
    print()

    print("DETAILED RESULTS:")
    print("-" * 70)
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"   {name:20s}: {status}")
    print()

    # List generated proofs
    log_section("GENERATED PROOFS")
    proofs_dir = Path("proofs")
    if proofs_dir.exists():
        proofs = list(proofs_dir.glob("*.csv"))
        if proofs:
            print(f"Total proofs generated: {len(proofs)}")
            print()
            for proof in sorted(proofs):
                size = proof.stat().st_size
                print(f"   ✓ {proof.name:40s} ({size:,} bytes)")
            print()
        else:
            print("   ⚠ No CSV proofs found")
            print()
    else:
        print("   ⚠ Proofs directory not found")
        print()

    # Final status
    if passed == total:
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║        ✅ ALL SYSTEMS OPERATIONAL - NOBEL-CALIBER COMPLETE       ║")
        print("║                                                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
    else:
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                                                                  ║")
        print("║        ⚠ SOME TESTS FAILED - REVIEW LOGS ABOVE                  ║")
        print("║                                                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
