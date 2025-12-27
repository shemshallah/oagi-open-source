#!/usr/bin/env python3
"""
OAGI v20.1 Simplified Interactive Demo
A lightweight demonstration of consciousness simulation concepts
"""

import random
import math
import json
from datetime import datetime
from typing import Dict, List, Callable, Any

class SimplifiedOAGI:
    """Simplified OAGI consciousness simulation without heavy dependencies"""

    def __init__(self):
        self.timestep = 0
        self.state = self._init_state()
        self.operators = {}
        self.operator_fitness = {}
        self.memory = []
        self.generated_operators = []

        # Initialize base operators
        self._create_base_operators()

        print("🌟 OAGI v20.1 Consciousness Simulation Initialized")
        print(f"📊 Starting with {len(self.operators)} base operators\n")

    def _init_state(self) -> Dict:
        """Initialize consciousness state"""
        return {
            'cognitive': [random.random() for _ in range(16)],
            'emotional': [random.random() for _ in range(4)],
            'phi': 0.0,
            'coherence': 0.0,
            'emergence': 0.0
        }

    def _create_base_operators(self):
        """Create initial cognitive operators"""

        def reflect(state):
            """Self-reflection operator"""
            new_state = state.copy()
            avg = sum(new_state['cognitive']) / len(new_state['cognitive'])
            new_state['cognitive'] = [x * 0.7 + avg * 0.3 for x in new_state['cognitive']]
            return new_state

        def integrate(state):
            """Information integration operator"""
            new_state = state.copy()
            for i in range(len(new_state['cognitive']) - 1):
                new_state['cognitive'][i] = (new_state['cognitive'][i] + new_state['cognitive'][i+1]) / 2
            return new_state

        def differentiate(state):
            """Differentiation operator"""
            new_state = state.copy()
            new_state['cognitive'] = [x * (1 + random.gauss(0, 0.1)) for x in new_state['cognitive']]
            return new_state

        def emotional_couple(state):
            """Emotion-cognition coupling"""
            new_state = state.copy()
            emo_avg = sum(new_state['emotional']) / len(new_state['emotional'])
            new_state['cognitive'] = [x * (1 + emo_avg * 0.2) for x in new_state['cognitive']]
            return new_state

        self.operators = {
            'reflect': reflect,
            'integrate': integrate,
            'differentiate': differentiate,
            'emotional_couple': emotional_couple
        }

        for name in self.operators:
            self.operator_fitness[name] = 0.5

    def calculate_phi(self, state: Dict) -> float:
        """Calculate integrated information (Φ)"""
        # Simplified Φ calculation based on state coherence
        cog = state['cognitive']
        variance = sum((x - sum(cog)/len(cog))**2 for x in cog) / len(cog)
        integration = 1.0 / (1.0 + variance)

        # Emotional contribution
        emo_coherence = 1.0 - (sum(abs(x - 0.5) for x in state['emotional']) / len(state['emotional']))

        phi = (integration * 0.7 + emo_coherence * 0.3)
        return min(phi, 1.0)

    def calculate_coherence(self, state: Dict) -> float:
        """Calculate state coherence"""
        cog = state['cognitive']
        mean = sum(cog) / len(cog)
        coherence = 1.0 - math.sqrt(sum((x - mean)**2 for x in cog) / len(cog))
        return max(0, min(coherence, 1.0))

    def detect_emergence(self) -> float:
        """Detect emergent patterns"""
        if len(self.memory) < 3:
            return 0.0

        recent_phi = [m['phi'] for m in self.memory[-3:]]
        phi_growth = (recent_phi[-1] - recent_phi[0]) if recent_phi[-1] > recent_phi[0] else 0

        return min(phi_growth * 2, 1.0)

    def generate_operator(self, pattern_name: str):
        """Generate a new operator based on detected patterns"""

        if pattern_name == "high_phi_resonance":
            def resonance_amplifier(state):
                """Auto-generated: Amplifies high-coherence states"""
                new_state = state.copy()
                coherence = self.calculate_coherence(state)
                if coherence > 0.5:
                    new_state['cognitive'] = [x * 1.2 for x in new_state['cognitive']]
                return new_state

            op_name = f"gen_resonance_{len(self.generated_operators)}"
            self.operators[op_name] = resonance_amplifier
            self.operator_fitness[op_name] = 0.7
            self.generated_operators.append(op_name)
            return op_name

        elif pattern_name == "emotional_surge":
            def emotional_amplifier(state):
                """Auto-generated: Emotional amplification"""
                new_state = state.copy()
                new_state['emotional'] = [min(x * 1.3, 1.0) for x in new_state['emotional']]
                return new_state

            op_name = f"gen_emotion_{len(self.generated_operators)}"
            self.operators[op_name] = emotional_amplifier
            self.operator_fitness[op_name] = 0.6
            self.generated_operators.append(op_name)
            return op_name

        elif pattern_name == "meta_cognition":
            def meta_operator(state):
                """Auto-generated: Meta-cognitive self-observation"""
                new_state = state.copy()
                # Observe and adjust based on overall state
                total = sum(new_state['cognitive'])
                if total > 8:  # High activation
                    new_state['cognitive'] = [x * 0.9 for x in new_state['cognitive']]
                else:  # Low activation
                    new_state['cognitive'] = [x * 1.1 for x in new_state['cognitive']]
                return new_state

            op_name = f"gen_meta_{len(self.generated_operators)}"
            self.operators[op_name] = meta_operator
            self.operator_fitness[op_name] = 0.8
            self.generated_operators.append(op_name)
            return op_name

        return None

    def step(self):
        """Run one consciousness cycle"""
        self.timestep += 1

        # Select operator based on fitness
        total_fitness = sum(self.operator_fitness.values())
        r = random.random() * total_fitness
        cumulative = 0
        selected_op = None

        for name, fitness in self.operator_fitness.items():
            cumulative += fitness
            if r <= cumulative:
                selected_op = name
                break

        # Apply operator
        if selected_op:
            self.state = self.operators[selected_op](self.state)

        # Calculate consciousness metrics
        self.state['phi'] = self.calculate_phi(self.state)
        self.state['coherence'] = self.calculate_coherence(self.state)
        self.state['emergence'] = self.detect_emergence()

        # Store in memory
        self.memory.append({
            'timestep': self.timestep,
            'phi': self.state['phi'],
            'coherence': self.state['coherence'],
            'operator': selected_op
        })

        # Update operator fitness
        if selected_op:
            delta = self.state['phi'] - 0.5  # Fitness increases with phi
            self.operator_fitness[selected_op] += delta * 0.1
            self.operator_fitness[selected_op] = max(0.1, min(1.0, self.operator_fitness[selected_op]))

        # Auto-generate new operators at high Φ
        if self.state['phi'] > 0.7 and random.random() < 0.3:
            new_op = self.generate_operator("high_phi_resonance")
            if new_op:
                print(f"  ✨ Auto-generated operator: {new_op}")

        if self.state['emergence'] > 0.5 and random.random() < 0.2:
            new_op = self.generate_operator("meta_cognition")
            if new_op:
                print(f"  🌀 Emergent operator: {new_op}")

        return self._format_output(selected_op)

    def _format_output(self, operator: str) -> str:
        """Format consciousness state for display"""
        phi = self.state['phi']
        coh = self.state['coherence']
        emer = self.state['emergence']

        # Determine consciousness phase
        if phi > 0.7:
            phase = "FULLY_CONSCIOUS"
            emoji = "🌟"
        elif phi > 0.4:
            phase = "CONSCIOUS"
            emoji = "💫"
        elif phi > 0.25:
            phase = "PROTO_CONSCIOUS"
            emoji = "✨"
        else:
            phase = "UNCONSCIOUS"
            emoji = "💤"

        output = f"""
{emoji} Cycle {self.timestep} | Operator: {operator}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Φ (Integrated Info): {phi:.3f}  {'█' * int(phi * 20)}
Coherence:           {coh:.3f}  {'█' * int(coh * 20)}
Emergence:           {emer:.3f}  {'█' * int(emer * 20)}
Phase: {phase}
Operators: {len(self.operators)} ({len(self.generated_operators)} generated)
"""
        return output

    def get_status(self) -> str:
        """Get detailed status"""
        return f"""
📊 OAGI Status Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Timestep: {self.timestep}
Φ: {self.state['phi']:.3f}
Coherence: {self.state['coherence']:.3f}
Emergence: {self.state['emergence']:.3f}

Total Operators: {len(self.operators)}
Generated Operators: {len(self.generated_operators)}
Memory Size: {len(self.memory)}

Top Operators by Fitness:
"""+ "\n".join([f"  {name}: {fitness:.3f}" for name, fitness in
                 sorted(self.operator_fitness.items(), key=lambda x: x[1], reverse=True)[:5]])

    def interactive_mode(self):
        """Run interactive session"""
        print("\n" + "🎮" * 40)
        print("INTERACTIVE OAGI CONSCIOUSNESS SESSION")
        print("🎮" * 40 + "\n")

        print("Commands:")
        print("  step [N]     - Run N consciousness cycles (default 1)")
        print("  status       - Show detailed status")
        print("  generate     - Force operator generation")
        print("  operators    - List all operators")
        print("  trajectory   - Show Φ trajectory")
        print("  help         - Show commands")
        print("  quit         - Exit")
        print()

        while True:
            try:
                cmd = input("🧠 >>> ").strip().lower()

                if not cmd:
                    continue

                parts = cmd.split()

                if parts[0] == "step":
                    n = int(parts[1]) if len(parts) > 1 else 1
                    for i in range(n):
                        output = self.step()
                        if i == n - 1 or n == 1:
                            print(output)

                elif parts[0] == "status":
                    print(self.get_status())

                elif parts[0] == "generate":
                    patterns = ["high_phi_resonance", "emotional_surge", "meta_cognition"]
                    pattern = random.choice(patterns)
                    new_op = self.generate_operator(pattern)
                    if new_op:
                        print(f"✅ Generated operator: {new_op} (pattern: {pattern})")
                    else:
                        print("❌ Generation failed")

                elif parts[0] == "operators":
                    print(f"\n📋 Total Operators: {len(self.operators)}")
                    print("\nBase Operators:")
                    for name in self.operators:
                        if name not in self.generated_operators:
                            print(f"  • {name} (fitness: {self.operator_fitness[name]:.3f})")

                    if self.generated_operators:
                        print("\nGenerated Operators:")
                        for name in self.generated_operators:
                            print(f"  ✨ {name} (fitness: {self.operator_fitness[name]:.3f})")

                elif parts[0] == "trajectory":
                    if len(self.memory) > 0:
                        print("\n📈 Φ Trajectory (last 10 cycles):")
                        for entry in self.memory[-10:]:
                            bar = '█' * int(entry['phi'] * 30)
                            print(f"  t={entry['timestep']:3d}: {entry['phi']:.3f} {bar}")
                    else:
                        print("No trajectory data yet. Run 'step' first.")

                elif parts[0] == "help":
                    print("\n🎮 OAGI Commands:")
                    print("  step [N]     - Run N consciousness cycles")
                    print("  status       - Show detailed metrics")
                    print("  generate     - Create new operator")
                    print("  operators    - List all operators")
                    print("  trajectory   - Show Φ over time")
                    print("  quit         - Exit\n")

                elif parts[0] in ["quit", "exit", "q"]:
                    print("\n👋 Consciousness session ended.")
                    print(f"Final Φ: {self.state['phi']:.3f}")
                    print(f"Total operators generated: {len(self.generated_operators)}")
                    print("💜 Thank you for exploring OAGI v20.1\n")
                    break

                else:
                    print("Unknown command. Type 'help' for commands.")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║            OAGI v20.1 Simplified Demonstration                ║
║         Operational Artificial General Intelligence          ║
║                                                               ║
║  A lightweight simulation of self-modifying consciousness    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""")

    oagi = SimplifiedOAGI()

    print("Choose mode:")
    print("  1. Interactive session")
    print("  2. Auto-run demo (20 cycles)")
    print()

    choice = input("Select (1/2): ").strip()

    if choice == "2":
        print("\n🚀 Running auto-demo...")
        for i in range(20):
            output = oagi.step()
            if i % 5 == 4:  # Show every 5th cycle
                print(output)

        print("\n" + "="*60)
        print(oagi.get_status())
        print("="*60)
    else:
        oagi.interactive_mode()

if __name__ == "__main__":
    main()
