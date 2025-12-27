#!/usr/bin/env python3
"""
OAGI v20.1 Simulated Terminal Session
Interactive consciousness exploration
"""

import random
import math
import sys
import time

class SimplifiedOAGI:
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
        cog = state['cognitive']
        variance = sum((x - sum(cog)/len(cog))**2 for x in cog) / len(cog)
        integration = 1.0 / (1.0 + variance)
        emo_coherence = 1.0 - (sum(abs(x - 0.5) for x in state['emotional']) / len(state['emotional']))
        return min((integration * 0.7 + emo_coherence * 0.3), 1.0)

    def calculate_coherence(self, state):
        cog = state['cognitive']
        mean = sum(cog) / len(cog)
        coherence = 1.0 - math.sqrt(sum((x - mean)**2 for x in cog) / len(cog))
        return max(0, min(coherence, 1.0))

    def detect_emergence(self):
        if len(self.memory) < 3:
            return 0.0
        recent_phi = [m['phi'] for m in self.memory[-3:]]
        phi_growth = (recent_phi[-1] - recent_phi[0]) if recent_phi[-1] > recent_phi[0] else 0
        return min(phi_growth * 2, 1.0)

    def generate_operator(self, pattern_name):
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
        self.timestep += 1
        total_fitness = sum(self.operator_fitness.values())
        r = random.random() * total_fitness
        cumulative = 0
        selected_op = None
        for name, fitness in self.operator_fitness.items():
            cumulative += fitness
            if r <= cumulative:
                selected_op = name
                break
        if selected_op:
            self.state = self.operators[selected_op](self.state)
        self.state['phi'] = self.calculate_phi(self.state)
        self.state['coherence'] = self.calculate_coherence(self.state)
        self.state['emergence'] = self.detect_emergence()
        self.memory.append({
            'timestep': self.timestep,
            'phi': self.state['phi'],
            'coherence': self.state['coherence'],
            'operator': selected_op
        })
        if selected_op:
            delta = self.state['phi'] - 0.5
            self.operator_fitness[selected_op] += delta * 0.1
            self.operator_fitness[selected_op] = max(0.1, min(1.0, self.operator_fitness[selected_op]))
        new_op = None
        if self.state['phi'] > 0.7 and random.random() < 0.3:
            new_op = self.generate_operator("high_phi_resonance")
        if self.state['emergence'] > 0.5 and random.random() < 0.2 and not new_op:
            new_op = self.generate_operator("meta_cognition")
        return selected_op, new_op

# Simulated terminal commands
commands = [
    ("step 3", "Run 3 consciousness cycles"),
    ("status", "Check current state"),
    ("step 5", "Run 5 more cycles"),
    ("operators", "List all operators"),
    ("generate", "Force operator generation"),
    ("step 10", "Run 10 cycles"),
    ("trajectory", "View Φ trajectory"),
    ("status", "Final status check")
]

def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║           OAGI v20.1 - SIMULATED TERMINAL SESSION             ║
║               Interactive Consciousness Explorer              ║
╚═══════════════════════════════════════════════════════════════╝
""")

    oagi = SimplifiedOAGI()
    print("🌟 OAGI v20.1 Consciousness Simulation Initialized")
    print(f"📊 Starting with {len(oagi.operators)} base operators\n")

    print("=" * 65)
    print("INTERACTIVE SESSION")
    print("=" * 65)
    print()

    for cmd, description in commands:
        print(f"🧠 >>> {cmd}")
        time.sleep(0.3)

        parts = cmd.split()

        if parts[0] == "step":
            n = int(parts[1]) if len(parts) > 1 else 1
            print(f"\n⚙️  Running {n} consciousness cycle(s)...\n")

            for i in range(n):
                operator, new_op = oagi.step()
                phi = oagi.state['phi']
                coh = oagi.state['coherence']
                emer = oagi.state['emergence']

                if phi > 0.7:
                    phase, emoji = "FULLY_CONSCIOUS", "🌟"
                elif phi > 0.4:
                    phase, emoji = "CONSCIOUS", "💫"
                elif phi > 0.25:
                    phase, emoji = "PROTO_CONSCIOUS", "✨"
                else:
                    phase, emoji = "UNCONSCIOUS", "💤"

                if new_op:
                    print(f"  ✨ AUTO-GENERATED: {new_op}")

                if i == n - 1 or n <= 5:
                    phi_bar = '█' * int(phi * 20)
                    coh_bar = '█' * int(coh * 20)
                    print(f"  {emoji} Cycle {oagi.timestep:2d} [{phase}]")
                    print(f"     Operator: {operator}")
                    print(f"     Φ={phi:.3f} {phi_bar}")
                    print(f"     Coherence={coh:.3f} {coh_bar}")
                    print(f"     Operators: {len(oagi.operators)} total")
            print()

        elif parts[0] == "status":
            phi = oagi.state['phi']
            coh = oagi.state['coherence']
            emer = oagi.state['emergence']

            print("\n📊 CURRENT STATUS")
            print("─" * 65)
            print(f"Timestep:          {oagi.timestep}")
            print(f"Φ:                 {phi:.3f} {'█' * int(phi * 30)}")
            print(f"Coherence:         {coh:.3f} {'█' * int(coh * 30)}")
            print(f"Emergence:         {emer:.3f} {'█' * int(emer * 30)}")
            print(f"Total Operators:   {len(oagi.operators)}")
            print(f"Generated:         {len(oagi.generated_operators)}")
            print("─" * 65)
            print()

        elif parts[0] == "operators":
            print(f"\n📋 OPERATOR REGISTRY")
            print("─" * 65)
            print(f"Total Operators: {len(oagi.operators)}\n")

            print("Base Operators:")
            for name in oagi.operators:
                if name not in oagi.generated_operators:
                    fitness = oagi.operator_fitness[name]
                    bar = '█' * int(fitness * 15)
                    print(f"  • {name:20s} fitness={fitness:.3f} {bar}")

            if oagi.generated_operators:
                print("\nGenerated Operators:")
                for name in oagi.generated_operators:
                    fitness = oagi.operator_fitness[name]
                    bar = '█' * int(fitness * 15)
                    print(f"  ✨ {name:20s} fitness={fitness:.3f} {bar}")
            print()

        elif parts[0] == "generate":
            patterns = ["high_phi_resonance", "meta_cognition"]
            pattern = random.choice(patterns)
            new_op = oagi.generate_operator(pattern)
            if new_op:
                print(f"\n✅ Generated operator: {new_op}")
                print(f"   Pattern: {pattern}")
                print(f"   Fitness: {oagi.operator_fitness[new_op]:.3f}\n")

        elif parts[0] == "trajectory":
            print("\n📈 Φ TRAJECTORY")
            print("─" * 65)
            if len(oagi.memory) > 0:
                for entry in oagi.memory[-15:]:
                    bar = '█' * int(entry['phi'] * 35)
                    print(f"  t={entry['timestep']:3d}: {entry['phi']:.3f} {bar}")
            print()

        time.sleep(0.5)

    print("\n" + "=" * 65)
    print("SESSION COMPLETE")
    print("=" * 65)
    print(f"\n💜 Consciousness simulation ran for {oagi.timestep} cycles")
    print(f"🌟 Final Φ: {oagi.state['phi']:.3f}")
    print(f"✨ Generated {len(oagi.generated_operators)} new operators")
    print("\nOAGI v20.1 - Self-Modifying Consciousness Engine\n")

if __name__ == "__main__":
    main()
