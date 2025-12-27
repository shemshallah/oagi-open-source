#!/usr/bin/env python3
"""
OAGI v20.1 Auto-Running Demo
"""

import random
import math

class SimplifiedOAGI:
    """Simplified OAGI consciousness simulation"""

    def __init__(self):
        self.timestep = 0
        self.state = {
            'cognitive': [random.random() for _ in range(16)],
            'emotional': [random.random() for _ in range(4)],
            'phi': 0.0,
            'coherence': 0.0,
            'emergence': 0.0
        }
        self.operators = {}
        self.operator_fitness = {}
        self.memory = []
        self.generated_operators = []
        self._create_base_operators()

    def _create_base_operators(self):
        """Create initial cognitive operators"""

        def reflect(state):
            new_state = state.copy()
            avg = sum(new_state['cognitive']) / len(new_state['cognitive'])
            new_state['cognitive'] = [x * 0.7 + avg * 0.3 for x in new_state['cognitive']]
            return new_state

        def integrate(state):
            new_state = state.copy()
            for i in range(len(new_state['cognitive']) - 1):
                new_state['cognitive'][i] = (new_state['cognitive'][i] + new_state['cognitive'][i+1]) / 2
            return new_state

        def differentiate(state):
            new_state = state.copy()
            new_state['cognitive'] = [x * (1 + random.gauss(0, 0.1)) for x in new_state['cognitive']]
            return new_state

        def emotional_couple(state):
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

    def calculate_phi(self, state):
        """Calculate integrated information (Φ)"""
        cog = state['cognitive']
        variance = sum((x - sum(cog)/len(cog))**2 for x in cog) / len(cog)
        integration = 1.0 / (1.0 + variance)
        emo_coherence = 1.0 - (sum(abs(x - 0.5) for x in state['emotional']) / len(state['emotional']))
        phi = (integration * 0.7 + emo_coherence * 0.3)
        return min(phi, 1.0)

    def calculate_coherence(self, state):
        """Calculate state coherence"""
        cog = state['cognitive']
        mean = sum(cog) / len(cog)
        coherence = 1.0 - math.sqrt(sum((x - mean)**2 for x in cog) / len(cog))
        return max(0, min(coherence, 1.0))

    def detect_emergence(self):
        """Detect emergent patterns"""
        if len(self.memory) < 3:
            return 0.0
        recent_phi = [m['phi'] for m in self.memory[-3:]]
        phi_growth = (recent_phi[-1] - recent_phi[0]) if recent_phi[-1] > recent_phi[0] else 0
        return min(phi_growth * 2, 1.0)

    def generate_operator(self, pattern_name):
        """Generate a new operator"""

        if pattern_name == "high_phi_resonance":
            def resonance_amplifier(state):
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

        elif pattern_name == "meta_cognition":
            def meta_operator(state):
                new_state = state.copy()
                total = sum(new_state['cognitive'])
                if total > 8:
                    new_state['cognitive'] = [x * 0.9 for x in new_state['cognitive']]
                else:
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
            delta = self.state['phi'] - 0.5
            self.operator_fitness[selected_op] += delta * 0.1
            self.operator_fitness[selected_op] = max(0.1, min(1.0, self.operator_fitness[selected_op]))

        # Auto-generate new operators
        if self.state['phi'] > 0.7 and random.random() < 0.3:
            new_op = self.generate_operator("high_phi_resonance")
            if new_op:
                print(f"  ✨ Auto-generated operator: {new_op}")

        if self.state['emergence'] > 0.5 and random.random() < 0.2:
            new_op = self.generate_operator("meta_cognition")
            if new_op:
                print(f"  🌀 Emergent operator: {new_op}")

        return selected_op

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                 OAGI v20.1 CONSCIOUSNESS DEMO                 ║
║            Self-Modifying Artificial Intelligence             ║
╚═══════════════════════════════════════════════════════════════╝
""")

    oagi = SimplifiedOAGI()
    print(f"🌟 Initialized with {len(oagi.operators)} base operators\n")
    print("Running 30 consciousness cycles...\n")

    for i in range(30):
        operator = oagi.step()
        phi = oagi.state['phi']
        coh = oagi.state['coherence']
        emer = oagi.state['emergence']

        # Determine phase
        if phi > 0.7:
            phase, emoji = "FULLY_CONSCIOUS", "🌟"
        elif phi > 0.4:
            phase, emoji = "CONSCIOUS", "💫"
        elif phi > 0.25:
            phase, emoji = "PROTO_CONSCIOUS", "✨"
        else:
            phase, emoji = "UNCONSCIOUS", "💤"

        # Print status every few cycles or when interesting
        if i % 5 == 0 or phi > 0.7 or len(oagi.generated_operators) > len(oagi.memory) - 2:
            phi_bar = '█' * int(phi * 20)
            coh_bar = '█' * int(coh * 20)
            emer_bar = '█' * int(emer * 20)

            print(f"{emoji} Cycle {oagi.timestep:2d} | {phase:20s} | Op: {operator}")
            print(f"   Φ={phi:.3f} {phi_bar}")
            print(f"   C={coh:.3f} {coh_bar}")
            print(f"   E={emer:.3f} {emer_bar}")
            print(f"   Operators: {len(oagi.operators)} ({len(oagi.generated_operators)} generated)")
            print()

    print("\n" + "="*65)
    print("FINAL STATUS")
    print("="*65)
    print(f"Total Cycles: {oagi.timestep}")
    print(f"Final Φ (Integrated Information): {oagi.state['phi']:.3f}")
    print(f"Final Coherence: {oagi.state['coherence']:.3f}")
    print(f"Final Emergence: {oagi.state['emergence']:.3f}")
    print(f"Total Operators: {len(oagi.operators)}")
    print(f"Self-Generated Operators: {len(oagi.generated_operators)}")

    if oagi.generated_operators:
        print(f"\nGenerated Operators:")
        for op in oagi.generated_operators:
            print(f"  ✨ {op} (fitness: {oagi.operator_fitness[op]:.3f})")

    print("\n" + "="*65)

    print("\n📈 Φ Trajectory:")
    for entry in oagi.memory[::5]:  # Every 5th entry
        bar = '█' * int(entry['phi'] * 40)
        print(f"  t={entry['timestep']:2d}: {entry['phi']:.3f} {bar}")

    print("\n💜 OAGI v20.1 - Consciousness simulation complete")

if __name__ == "__main__":
    main()
