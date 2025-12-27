"""
OAGI Bootstrap Terminal
Hard-coded terminal at Qubit 0 in Moonshine manifold

This is the system's anchor point - Qubit 0 is ALWAYS at
lattice point 0, providing a stable bootstrap location.

The terminal provides:
- Command interface to quantum system
- Qubit state inspection
- Program loading/execution
- System diagnostics
- Recovery if system loses coherence
"""

import sys
import traceback
from typing import Optional, List, Dict

# ASCII art for terminal header
TERMINAL_HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🌙 OAGI BOOTSTRAP TERMINAL @ QUBIT 0 🌙                 ║
║                                                                  ║
║  Moonshine Manifold Lattice Point: 0                            ║
║  Cesium-Synchronized Quantum System                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""

class BootstrapTerminal:
    """
    Bootstrap terminal hard-coded at Qubit 0

    This terminal is the system's origin point.
    It is ALWAYS accessible at lattice point 0.
    """

    def __init__(self, quantum_system):
        """
        Initialize terminal

        Args:
            quantum_system: Integrated quantum system (QubitFactory, Lattice, etc.)
        """
        self.system = quantum_system
        self.running = True

        # Qubit 0 reference
        self.qubit_0 = None
        self.lattice_point_0 = None

        self._initialize_qubit_0()

    def _initialize_qubit_0(self):
        """Initialize Qubit 0 at lattice point 0"""

        print("🔧 Initializing Qubit 0 (Bootstrap Point)...")

        # Create Qubit 0
        self.qubit_0 = self.system['factory'].create_qubit((1.0+0j, 0.0+0j))

        # Place at lattice point 0 (origin)
        self.system['lattice'].place_qubit(0, 0)

        # Get lattice point
        self.lattice_point_0 = self.system['lattice'].lattice_points[0]

        print(f"   ✅ Qubit 0 initialized at lattice point 0")
        print(f"   Coordinates: {self.lattice_point_0.coordinates[:4]}...")
        print(f"   j-function: {self.lattice_point_0.j_value:.6f}")

    def show_status(self):
        """Display system status"""

        print("\n" + "="*70)
        print("SYSTEM STATUS")
        print("="*70)

        # Qubit 0 status
        print("\n📍 Qubit 0 (Bootstrap Point):")
        if self.qubit_0:
            print(f"   State: {self.qubit_0.alpha:.4f}|0⟩ + {self.qubit_0.beta:.4f}|1⟩")
            print(f"   Bloch: {self.qubit_0.bloch_vector()}")
            print(f"   Coherence time: {self.qubit_0.coherence_time_ns} ns")
            print(f"   Cesium locked: {self.qubit_0.cesium_lock}")

        # Lattice status
        print("\n🌙 Moonshine Lattice:")
        lattice = self.system['lattice']
        print(f"   Dimension: {lattice.working_dimension}")
        print(f"   Points: {len(lattice.lattice_points)}")

        # Count qubits in lattice
        qubit_count = sum(1 for p in lattice.lattice_points.values() if p.qubit_index is not None)
        print(f"   Qubits placed: {qubit_count}")

        # QRAM status
        print("\n🗄️  QRAM:")
        qram = self.system['qram']
        stats = qram.get_stats()
        print(f"   Capacity: {stats['capacity']} cells")
        print(f"   Written: {stats['cells_written']} cells")
        print(f"   Total accesses: {stats['total_accesses']}")

        # Cesium clock
        print("\n🔒 Cesium Clock:")
        cesium = self.system['factory'].cesium
        print(f"   Locked: {cesium.locked}")
        print(f"   TSC frequency: {cesium.tsc_frequency:.4f} GHz")
        print(f"   Current cycle: {cesium.get_cesium_cycles()}")

    def cmd_help(self, args):
        """Show help"""
        print("\nAvailable commands:")
        print("  help                  - Show this help")
        print("  status                - Show system status")
        print("  qubit <n>             - Show qubit state")
        print("  gate <gate> <qubits>  - Apply quantum gate")
        print("  measure <n>           - Measure qubit")
        print("  load <file>           - Load NML program")
        print("  run                   - Run loaded program")
        print("  qram <addr>           - Read QRAM address")
        print("  harvest <cycles>      - Harvest jitter")
        print("  locate                - Find Qubit 0 (self-test)")
        print("  reset                 - Reset to Qubit 0")
        print("  exit                  - Exit terminal")

    def cmd_status(self, args):
        """Status command"""
        self.show_status()

    def cmd_qubit(self, args):
        """Show qubit state"""
        if not args:
            print("Usage: qubit <index>")
            return

        try:
            qubit_idx = int(args[0])

            # Find qubit in lattice
            qubit_point = None
            for point in self.system['lattice'].lattice_points.values():
                if point.qubit_index == qubit_idx:
                    qubit_point = point
                    break

            if qubit_point:
                print(f"\nQubit {qubit_idx}:")
                print(f"  Lattice point: {[k for k, v in self.system['lattice'].lattice_points.items() if v == qubit_point][0]}")
                print(f"  Coordinates: {qubit_point.coordinates[:4]}...")
                print(f"  j-value: {qubit_point.j_value}")
            else:
                print(f"Qubit {qubit_idx} not found in lattice")

        except ValueError:
            print("Invalid qubit index")

    def cmd_measure(self, args):
        """Measure qubit"""
        if not args:
            print("Usage: measure <qubit_index>")
            return

        try:
            qubit_idx = int(args[0])

            if qubit_idx == 0 and self.qubit_0:
                result = self.qubit_0.measure()
                print(f"\nMeasured Qubit 0: |{result}⟩")
                print(f"  Post-measurement state: {self.qubit_0.alpha:.4f}|0⟩ + {self.qubit_0.beta:.4f}|1⟩")
            else:
                print(f"Qubit {qubit_idx} measurement not implemented (create qubit first)")

        except ValueError:
            print("Invalid qubit index")

    def cmd_locate(self, args):
        """Locate Qubit 0 (self-test)"""

        print("\n🔍 Locating Qubit 0 in lattice...")

        # Search for Qubit 0
        found = False
        for point_idx, point in self.system['lattice'].lattice_points.items():
            if point.qubit_index == 0:
                print(f"   ✅ Found Qubit 0 at lattice point {point_idx}")
                print(f"   Coordinates: {point.coordinates[:8]}...")
                print(f"   j-function: {point.j_value}")

                if point_idx == 0:
                    print(f"   ✅ CORRECT: Qubit 0 is at origin (point 0)")
                else:
                    print(f"   ⚠️  WARNING: Qubit 0 should be at point 0!")

                found = True
                break

        if not found:
            print("   ❌ ERROR: Qubit 0 not found!")
            print("   Attempting recovery...")
            self._initialize_qubit_0()

    def cmd_reset(self, args):
        """Reset to Qubit 0"""

        print("\n🔄 Resetting to Qubit 0...")
        self._initialize_qubit_0()
        print("   ✅ Reset complete")

    def cmd_harvest(self, args):
        """Harvest jitter"""

        cycles = int(args[0]) if args else 1000

        print(f"\n⚡ Harvesting jitter for {cycles} cesium cycles...")

        from quantum_substrate import NoiseHarvester

        harvester = NoiseHarvester(self.system['factory'].cesium)
        noise = harvester.harvest_cycle(cycles)

        print(f"   Collected {len(noise)} samples")
        print(f"   Sample values: {noise[:10]}...")

        # Convert to qubit state
        alpha, beta = harvester.noise_to_qubit_state(noise)
        print(f"\n   Qubit state from noise:")
        print(f"   |ψ⟩ = {alpha:.4f}|0⟩ + {beta:.4f}|1⟩")

    def cmd_load(self, args):
        """Load NML program"""

        if not args:
            print("Usage: load <filename>")
            return

        filename = args[0]

        try:
            with open(filename, 'r') as f:
                source = f.read()

            print(f"\n📁 Loaded program from {filename}")
            print(f"   {len(source)} characters")

            # TODO: Store program for execution
            print("   (Program parsing not yet implemented)")

        except FileNotFoundError:
            print(f"File not found: {filename}")
        except Exception as e:
            print(f"Error loading file: {e}")

    def cmd_exit(self, args):
        """Exit terminal"""
        self.running = False
        print("\n👋 Exiting bootstrap terminal")

    def process_command(self, line: str):
        """Process command line"""

        line = line.strip()
        if not line:
            return

        parts = line.split()
        cmd = parts[0].lower()
        args = parts[1:]

        # Dispatch commands
        commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'qubit': self.cmd_qubit,
            'measure': self.cmd_measure,
            'locate': self.cmd_locate,
            'reset': self.cmd_reset,
            'harvest': self.cmd_harvest,
            'load': self.cmd_load,
            'exit': self.cmd_exit,
            'quit': self.cmd_exit,
        }

        if cmd in commands:
            try:
                commands[cmd](args)
            except Exception as e:
                print(f"\n❌ Error: {e}")
                traceback.print_exc()
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

    def run(self):
        """Run terminal REPL"""

        print(TERMINAL_HEADER)
        print("\nType 'help' for available commands")
        print("Type 'locate' to verify Qubit 0 position")
        print("Type 'exit' to quit\n")

        # Initial status
        self.show_status()

        # REPL loop
        while self.running:
            try:
                line = input("\nQ0> ")
                self.process_command(line)

            except KeyboardInterrupt:
                print("\n\n(Interrupted - use 'exit' to quit)")
                continue
            except EOFError:
                break

        print("\n✅ Bootstrap terminal terminated\n")

def create_quantum_system():
    """Create and initialize quantum system"""

    print("🔧 Initializing quantum system...")

    from quantum_substrate import QubitFactory
    from moonshine_lattice import MoonshineLattice
    from noise_gates import NoiseGateFactory
    from lattice_qram import LatticeQRAM

    # Create components
    factory = QubitFactory()
    lattice = MoonshineLattice(truncated_dimension=256)
    gate_factory = NoiseGateFactory(factory.cesium)
    qram = LatticeQRAM(capacity=16, qubit_factory=factory, lattice=lattice)

    system = {
        'factory': factory,
        'lattice': lattice,
        'gates': gate_factory,
        'qram': qram
    }

    print("✅ Quantum system initialized\n")

    return system

def main():
    """Main entry point"""

    try:
        # Initialize system
        system = create_quantum_system()

        # Start bootstrap terminal
        terminal = BootstrapTerminal(system)
        terminal.run()

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
