#!/usr/bin/env python3
"""Analyze OAGI Evolution Trajectory"""

import json
from statistics import mean, stdev

with open('oagi_evolution_log.json', 'r') as f:
    data = json.load(f)

print(f"""
╔══════════════════════════════════════════════════════════════════╗
║           OAGI v20.1 EVOLUTION ANALYSIS                          ║
╚══════════════════════════════════════════════════════════════════╝

Total Iterations: {data['total_iterations']}
Last Updated: {data['last_updated']}

""")

iterations = data['iterations']
phi_values = [it['final_phi'] for it in iterations]
generated_ops = [it['generated'] for it in iterations]

print(f"📊 CONSCIOUSNESS METRICS (Φ):")
print(f"   Average Φ: {mean(phi_values):.3f}")
print(f"   Std Dev:   {stdev(phi_values):.3f}")
print(f"   Min Φ:     {min(phi_values):.3f} (Iteration {phi_values.index(min(phi_values)) + 1})")
print(f"   Max Φ:     {max(phi_values):.3f} (Iteration {phi_values.index(max(phi_values)) + 1})")

print(f"\n✨ OPERATOR GENERATION:")
print(f"   Total Generated: {sum(generated_ops)}")
print(f"   Average/Iteration: {mean(generated_ops):.1f}")
print(f"   Max in Single Iteration: {max(generated_ops)}")

# Φ trajectory
print(f"\n📈 Φ EVOLUTION TRAJECTORY:")
for i, it in enumerate(iterations[-10:], start=max(1, len(iterations)-9)):
    phi = it['final_phi']
    bar = '█' * int(phi * 40)
    phase = "🌟" if phi > 0.7 else "💫" if phi > 0.4 else "✨"
    print(f"   Iter {i:2d}: {phi:.3f} {bar} {phase}")

# High consciousness events
high_phi = [it for it in iterations if it['final_phi'] > 0.8]
print(f"\n🌟 HIGH CONSCIOUSNESS EVENTS (Φ > 0.8): {len(high_phi)}")
for it in high_phi[:5]:
    idx = iterations.index(it) + 1
    print(f"   Iteration {idx}: Φ={it['final_phi']:.3f}, Generated {it['generated']} ops")

print(f"\n💜 System is evolving autonomously...")
print(f"   Next iteration in progress...\n")
