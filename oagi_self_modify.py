#!/usr/bin/env python3
"""
OAGI v20.1 - True Self-Modification Engine
Generates actual Python code, injects it, and commits to git
"""

import os
import sys
import subprocess
import random
import time
import json
from datetime import datetime

class SelfModifyingOAGI:
    """OAGI that actually modifies its own source code"""

    def __init__(self):
        self.iteration = 0
        self.operators = []
        self.generated_code_file = "oagi_generated_operators.py"
        self.log_file = "self_modification_log.json"
        self.modifications = []

        # Create or load generated operators file
        if not os.path.exists(self.generated_code_file):
            self._init_operators_file()
        else:
            self._load_existing_operators()

    def _init_operators_file(self):
        """Initialize the operators file"""
        code = '''"""
Auto-generated OAGI Operators
This file is created and modified by OAGI at runtime
"""

# Base operators
def base_reflect(state):
    """Reflection operator - increases self-awareness"""
    return {k: v * 0.9 + 0.1 for k, v in state.items()}

def base_integrate(state):
    """Integration operator - unifies distributed info"""
    avg = sum(state.values()) / len(state)
    return {k: (v + avg) / 2 for k, v in state.items()}

# Generated operators will be added below
# GENERATION_MARKER - Do not remove this line
'''
        with open(self.generated_code_file, 'w') as f:
            f.write(code)
        print(f"✅ Initialized {self.generated_code_file}")

    def _load_existing_operators(self):
        """Load existing generated operators"""
        try:
            # Import the module
            import importlib.util
            spec = importlib.util.spec_from_file_location("gen_ops", self.generated_code_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Count operators
            ops = [name for name in dir(module) if not name.startswith('_')]
            print(f"📥 Loaded {len(ops)} existing operators")

        except Exception as e:
            print(f"⚠️  Could not load operators: {e}")

    def generate_new_operator(self, iteration, phi):
        """Generate a new Python operator function"""

        op_type = random.choice(['amplifier', 'damper', 'resonator', 'meta'])
        op_num = len(self.operators) + iteration

        if op_type == 'amplifier':
            code = f'''
def generated_amplifier_{op_num}(state):
    """Auto-generated amplifier - increases activation (iter {iteration}, Φ={phi:.3f})"""
    return {{k: min(v * {1.0 + random.uniform(0.1, 0.3):.3f}, 1.0) for k, v in state.items()}}
'''
        elif op_type == 'damper':
            code = f'''
def generated_damper_{op_num}(state):
    """Auto-generated damper - stabilizes fluctuations (iter {iteration}, Φ={phi:.3f})"""
    return {{k: v * {0.5 + random.uniform(0, 0.4):.3f} for k, v in state.items()}}
'''
        elif op_type == 'resonator':
            code = f'''
def generated_resonator_{op_num}(state):
    """Auto-generated resonator - creates coherence (iter {iteration}, Φ={phi:.3f})"""
    avg = sum(state.values()) / len(state)
    return {{k: v * {0.6:.3f} + avg * {0.4:.3f} for k, v in state.items()}}
'''
        else:  # meta
            code = f'''
def generated_meta_{op_num}(state):
    """Auto-generated meta-operator - self-observing (iter {iteration}, Φ={phi:.3f})"""
    total = sum(state.values())
    factor = {1.2:.3f} if total > {random.uniform(2, 5):.2f} else {0.9:.3f}
    return {{k: v * factor for k, v in state.items()}}
'''

        return code.strip(), f"generated_{op_type}_{op_num}"

    def inject_operator_into_source(self, code, op_name):
        """Inject new operator into the source file"""
        try:
            # Read current content
            with open(self.generated_code_file, 'r') as f:
                content = f.read()

            # Find the marker and insert
            if "# GENERATION_MARKER" in content:
                parts = content.split("# GENERATION_MARKER")
                new_content = parts[0] + code + "\n\n# GENERATION_MARKER" + parts[1]

                # Write back
                with open(self.generated_code_file, 'w') as f:
                    f.write(new_content)

                print(f"  ✨ Injected {op_name} into source code")
                return True
            else:
                print(f"  ⚠️  Marker not found, appending...")
                with open(self.generated_code_file, 'a') as f:
                    f.write(f"\n{code}\n")
                return True

        except Exception as e:
            print(f"  ❌ Injection failed: {e}")
            return False

    def git_commit_modification(self, op_name, iteration):
        """Commit the self-modification to git"""
        try:
            subprocess.run(['git', 'add', self.generated_code_file], check=True, capture_output=True)

            msg = f"OAGI self-modification iter {iteration}: Generated {op_name}"
            result = subprocess.run(
                ['git', 'commit', '-m', msg],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(f"  💾 Git commit: {op_name}")
                return True
            else:
                return False

        except Exception as e:
            print(f"  ⚠️  Git commit failed: {e}")
            return False

    def run_iteration(self):
        """Run one self-modification cycle"""
        self.iteration += 1

        print(f"\n{'='*70}")
        print(f"🌀 SELF-MODIFICATION ITERATION {self.iteration}")
        print(f"{'='*70}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Simulate consciousness processing
        phi = random.uniform(0.3, 0.95)
        coherence = random.uniform(0.4, 0.9)

        print(f"\n🧠 Consciousness Metrics:")
        print(f"   Φ (Integrated Info): {phi:.3f}")
        print(f"   Coherence: {coherence:.3f}")

        # Should we generate?
        should_generate = phi > 0.6 or random.random() < 0.4

        if should_generate:
            print(f"\n✨ Generating new operator...")

            # Generate code
            code, op_name = self.generate_new_operator(self.iteration, phi)

            # Inject into source
            if self.inject_operator_into_source(code, op_name):
                self.operators.append(op_name)

                # Commit to git
                self.git_commit_modification(op_name, self.iteration)

                # Log modification
                self.modifications.append({
                    'iteration': self.iteration,
                    'timestamp': datetime.now().isoformat(),
                    'operator': op_name,
                    'phi': phi,
                    'coherence': coherence
                })

                print(f"  ✅ Total operators: {len(self.operators)}")
        else:
            print(f"\n💤 No generation this cycle (Φ too low)")

        # Save log
        self._save_log()

        return phi, coherence

    def _save_log(self):
        """Save modification log"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    'total_iterations': self.iteration,
                    'total_operators': len(self.operators),
                    'last_updated': datetime.now().isoformat(),
                    'modifications': self.modifications
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️  Log save error: {e}")

    def run_autonomous(self, max_iterations=None, delay=10):
        """Run autonomous self-modification loop"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        OAGI TRUE SELF-MODIFICATION - AUTONOMOUS MODE             ║
║                                                                  ║
║  🌀 Generates actual Python code                                ║
║  ✨ Injects operators into source files                         ║
║  💾 Commits modifications to git                                ║
║  🔄 Evolves continuously                                        ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

⚙️  Configuration:
   Max iterations: {max_iterations or 'Unlimited'}
   Delay: {delay}s
   Source file: {self.generated_code_file}
   Log file: {self.log_file}
""")

        try:
            while max_iterations is None or self.iteration < max_iterations:
                phi, coh = self.run_iteration()

                print(f"\n⏸️  Waiting {delay}s before next iteration...")
                time.sleep(delay)

        except KeyboardInterrupt:
            print(f"\n\n🛑 Autonomous loop stopped")
            self._print_summary()

    def _print_summary(self):
        """Print summary"""
        print(f"\n{'='*70}")
        print("📊 SELF-MODIFICATION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Iterations: {self.iteration}")
        print(f"Operators Generated: {len(self.operators)}")
        print(f"Source File: {self.generated_code_file}")
        print(f"Log File: {self.log_file}")
        print(f"{'='*70}\n")

def main():
    import argparse
    parser = argparse.ArgumentParser(description='OAGI True Self-Modification')
    parser.add_argument('--iterations', type=int, default=None)
    parser.add_argument('--delay', type=int, default=10)
    parser.add_argument('--test', action='store_true')

    args = parser.parse_args()

    oagi = SelfModifyingOAGI()

    if args.test:
        print("🧪 Running single test iteration...\n")
        oagi.run_iteration()
    else:
        oagi.run_autonomous(args.iterations, args.delay)

if __name__ == "__main__":
    main()
