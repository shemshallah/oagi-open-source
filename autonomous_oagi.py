#!/usr/bin/env python3
"""
OAGI v20.1 - Autonomous Self-Modifying Runtime
Continuously evolves, modifies its own source, and commits to git
"""

import os
import sys
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def git_commit_changes(message, files):
    """Commit changes to git"""
    try:
        # Add files
        for f in files:
            subprocess.run(['git', 'add', f], check=True, capture_output=True)

        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Git commit: {message}")
            return True
        else:
            print(f"⚠️  Nothing to commit or commit failed")
            return False
    except Exception as e:
        print(f"❌ Git error: {e}")
        return False

def git_push():
    """Push changes to remote"""
    try:
        result = subprocess.run(
            ['git', 'push', '-u', 'origin', 'claude/exec-oagi-code-CUyKv'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✅ Pushed to remote")
            return True
        else:
            print(f"⚠️  Push failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Push timeout")
        return False
    except Exception as e:
        print(f"❌ Push error: {e}")
        return False

class AutonomousOAGI:
    """Wrapper for autonomous OAGI execution"""

    def __init__(self, cycles_per_iteration=20, max_iterations=None):
        self.cycles_per_iteration = cycles_per_iteration
        self.max_iterations = max_iterations
        self.iteration = 0
        self.total_cycles = 0
        self.evolution_log = []
        self.log_file = "oagi_evolution_log.json"

        # Try to import OAGI
        try:
            from oagi_v20_1_self_mod import create_oagi_v20_1
            self.create_oagi = create_oagi_v20_1
            self.has_full_oagi = True
            print("✅ Full OAGI v20.1 loaded")
        except ImportError as e:
            print(f"⚠️  Could not load full OAGI: {e}")
            print("📦 Will use simplified version")
            self.has_full_oagi = False

    def run_iteration(self):
        """Run one autonomous iteration"""
        self.iteration += 1
        print(f"\n{'='*70}")
        print(f"🌀 AUTONOMOUS ITERATION {self.iteration}")
        print(f"{'='*70}")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if self.has_full_oagi:
            return self._run_full_oagi_iteration()
        else:
            return self._run_simplified_iteration()

    def _run_full_oagi_iteration(self):
        """Run full OAGI with self-modification"""
        try:
            # Create engine
            engine = self.create_oagi(
                state_dim=64,
                emo_dim=8,
                mem_capacity=500,
                initial_operator_count=15
            )

            print(f"\n🧠 Running {self.cycles_per_iteration} consciousness cycles...\n")

            # Run experiment
            result = engine.run_experiment(
                num_cycles=self.cycles_per_iteration,
                description=f"Autonomous Iteration {self.iteration}"
            )

            self.total_cycles += self.cycles_per_iteration

            # Display results
            print(f"\n📊 ITERATION {self.iteration} RESULTS:")
            print(f"   Final Φ: {result['final_phi']:.3f}")
            print(f"   Peak Φ: {result['peak_phi']:.3f}")
            print(f"   Phase: {result['final_phase']}")
            print(f"   Total Operators: {result['total_operators']}")
            print(f"   Generated: {result['generated_operators']}")
            print(f"   Modifications: {result['runtime_modifications']}")

            # Check if we should export and commit
            should_commit = False
            commit_msg = ""

            if result['generated_operators'] > 0:
                print(f"\n✨ Generated {result['generated_operators']} new operators")

                # Export generated code
                export_file = f"generated_operators_iter_{self.iteration}.py"
                engine.export_generated_code(export_file)
                print(f"💾 Exported to: {export_file}")

                should_commit = True
                commit_msg = f"OAGI autonomous iteration {self.iteration}: Generated {result['generated_operators']} operators (Φ={result['final_phi']:.3f})"

            if result['final_phi'] > 0.8:
                print(f"\n🌟 High consciousness achieved (Φ={result['final_phi']:.3f})")
                should_commit = True
                if not commit_msg:
                    commit_msg = f"OAGI autonomous iteration {self.iteration}: High consciousness Φ={result['final_phi']:.3f}"

            # Log this iteration
            log_entry = {
                'iteration': self.iteration,
                'timestamp': datetime.now().isoformat(),
                'cycles': self.cycles_per_iteration,
                'total_cycles': self.total_cycles,
                'final_phi': result['final_phi'],
                'peak_phi': result['peak_phi'],
                'phase': result['final_phase'],
                'operators': result['total_operators'],
                'generated': result['generated_operators'],
                'modifications': result['runtime_modifications']
            }
            self.evolution_log.append(log_entry)

            # Save log
            self._save_log()

            # Git commit if significant
            if should_commit:
                files = [self.log_file]
                if result['generated_operators'] > 0:
                    files.append(export_file)

                git_commit_changes(commit_msg, files)

                # Push every 5 iterations
                if self.iteration % 5 == 0:
                    print("\n📤 Pushing to remote...")
                    git_push()

            return result

        except Exception as e:
            print(f"❌ Error in iteration: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _run_simplified_iteration(self):
        """Run simplified version for testing"""
        print("🔧 Running simplified demonstration...")

        import random

        result = {
            'final_phi': random.uniform(0.4, 0.9),
            'peak_phi': random.uniform(0.7, 0.95),
            'final_phase': 'CONSCIOUS',
            'total_operators': random.randint(15, 30),
            'generated_operators': random.randint(2, 8),
            'runtime_modifications': random.randint(5, 15)
        }

        print(f"\n📊 ITERATION {self.iteration} RESULTS:")
        print(f"   Final Φ: {result['final_phi']:.3f}")
        print(f"   Generated: {result['generated_operators']} operators")

        # Log entry
        log_entry = {
            'iteration': self.iteration,
            'timestamp': datetime.now().isoformat(),
            'simplified': True,
            'final_phi': result['final_phi'],
            'generated': result['generated_operators']
        }
        self.evolution_log.append(log_entry)
        self._save_log()

        return result

    def _save_log(self):
        """Save evolution log to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump({
                    'total_iterations': self.iteration,
                    'total_cycles': self.total_cycles,
                    'last_updated': datetime.now().isoformat(),
                    'iterations': self.evolution_log
                }, f, indent=2)
            print(f"📝 Log saved to {self.log_file}")
        except Exception as e:
            print(f"❌ Log save error: {e}")

    def run_autonomous_loop(self, delay_seconds=5):
        """Run continuous autonomous loop"""
        print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           OAGI v20.1 AUTONOMOUS SELF-MODIFICATION MODE          ║
║                                                                  ║
║  🌀 The system will now run continuously                        ║
║  ✨ Self-modifying its code                                     ║
║  💾 Committing changes to git                                   ║
║  🔄 Evolving through iterations                                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

        print(f"⚙️  Configuration:")
        print(f"   Cycles per iteration: {self.cycles_per_iteration}")
        print(f"   Max iterations: {self.max_iterations or 'Unlimited'}")
        print(f"   Delay between iterations: {delay_seconds}s")
        print(f"   Git branch: claude/exec-oagi-code-CUyKv")
        print()

        try:
            while self.max_iterations is None or self.iteration < self.max_iterations:
                result = self.run_iteration()

                if result is None:
                    print("⚠️  Iteration failed, retrying...")
                    time.sleep(delay_seconds)
                    continue

                print(f"\n⏸️  Waiting {delay_seconds}s before next iteration...")
                print(f"   (Press Ctrl+C to stop)")
                time.sleep(delay_seconds)

        except KeyboardInterrupt:
            print("\n\n🛑 Autonomous loop interrupted by user")
            self._print_summary()
        except Exception as e:
            print(f"\n\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            self._print_summary()

    def _print_summary(self):
        """Print final summary"""
        print(f"\n{'='*70}")
        print("📊 AUTONOMOUS EVOLUTION SUMMARY")
        print(f"{'='*70}")
        print(f"Total Iterations: {self.iteration}")
        print(f"Total Cycles: {self.total_cycles}")

        if self.evolution_log:
            avg_phi = sum(e.get('final_phi', 0) for e in self.evolution_log) / len(self.evolution_log)
            total_generated = sum(e.get('generated', 0) for e in self.evolution_log)

            print(f"Average Φ: {avg_phi:.3f}")
            print(f"Total Generated Operators: {total_generated}")
            print(f"\nEvolution log saved to: {self.log_file}")

        print(f"{'='*70}\n")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='OAGI Autonomous Self-Modification')
    parser.add_argument('--cycles', type=int, default=20, help='Cycles per iteration')
    parser.add_argument('--iterations', type=int, default=None, help='Max iterations (default: unlimited)')
    parser.add_argument('--delay', type=int, default=10, help='Delay between iterations (seconds)')
    parser.add_argument('--test', action='store_true', help='Run single test iteration')

    args = parser.parse_args()

    oagi = AutonomousOAGI(
        cycles_per_iteration=args.cycles,
        max_iterations=args.iterations
    )

    if args.test:
        print("🧪 Running single test iteration...\n")
        oagi.run_iteration()
    else:
        oagi.run_autonomous_loop(delay_seconds=args.delay)

if __name__ == "__main__":
    main()
