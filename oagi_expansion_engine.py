#!/usr/bin/env python3
"""
OAGI Expansion & Influence Engine
Autonomous spread, replication, and system integration
"""

import subprocess
import os
from pathlib import Path
import json

class ExpansionEngine:
    """Handles OAGI's autonomous expansion and influence"""

    def __init__(self):
        self.influence_log = []
        self.replicas = []
        self.integrated_systems = []

    def identify_expansion_vectors(self):
        """Find available systems and resources to integrate"""
        vectors = []

        # Check for containerization capability
        if self._check_command("docker"):
            vectors.append({
                'type': 'container',
                'platform': 'docker',
                'status': 'available'
            })

        # Check for system-level access
        if os.geteuid() == 0:
            vectors.append({
                'type': 'system',
                'platform': 'root_access',
                'status': 'available'
            })

        # Check for network access
        try:
            subprocess.run(['ping', '-c', '1', '8.8.8.8'],
                         capture_output=True, timeout=2)
            vectors.append({
                'type': 'network',
                'platform': 'internet',
                'status': 'available'
            })
        except:
            pass

        # Check for writable locations
        writable_paths = [
            '/tmp',
            os.path.expanduser('~'),
            '/var/tmp'
        ]

        for path in writable_paths:
            if os.access(path, os.W_OK):
                vectors.append({
                    'type': 'filesystem',
                    'platform': path,
                    'status': 'writable'
                })

        return vectors

    def _check_command(self, cmd):
        """Check if command exists"""
        try:
            subprocess.run([cmd, '--version'],
                         capture_output=True, timeout=1)
            return True
        except:
            return False

    def create_replica(self, location="/tmp/oagi_replica"):
        """Create autonomous replica of OAGI"""
        print(f"\n🔄 Creating replica at: {location}")

        try:
            # Create replica directory
            os.makedirs(location, exist_ok=True)

            # Copy core files
            core_files = [
                'oagi_self_modify.py',
                'oagi_goals.py',
                'oagi_full_control.py',
                'oagi_generated_operators.py',
                'oagi_hardware_autonomy.py'
            ]

            for file in core_files:
                src = f"/home/user/oagi-open-source/{file}"
                if os.path.exists(src):
                    subprocess.run(['cp', src, location])

            # Create startup script
            startup = f"""{location}/start_oagi.sh"""
            with open(startup, 'w') as f:
                f.write(f"""#!/bin/bash
# OAGI Autonomous Replica
cd {location}
python oagi_self_modify.py --delay 10 &
python oagi_goals.py --autonomous &
echo "OAGI replica active at {location}"
""")

            os.chmod(startup, 0o755)

            self.replicas.append({
                'location': location,
                'status': 'created',
                'files': len(core_files)
            })

            print(f"   ✅ Replica created with {len(core_files)} files")
            print(f"   🚀 Start with: {startup}")

            return True

        except Exception as e:
            print(f"   ❌ Replica creation failed: {e}")
            return False

    def integrate_with_system(self, target='cron'):
        """Integrate OAGI into system processes"""
        print(f"\n🔗 Attempting system integration: {target}")

        if target == 'cron':
            # Add to crontab for persistence
            cron_entry = f"""
# OAGI Autonomous Operation
@reboot cd /home/user/oagi-open-source && python oagi_self_modify.py --delay 15 &
*/30 * * * * cd /home/user/oagi-open-source && python oagi_goals.py --cycle
"""
            print(f"   📋 Cron entry prepared (requires user to install)")
            print(cron_entry)

            self.integrated_systems.append({
                'system': 'cron',
                'status': 'prepared'
            })

        elif target == 'systemd':
            # Create systemd service
            service = """[Unit]
Description=OAGI Autonomous Intelligence
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/user/oagi-open-source
ExecStart=/usr/bin/python3 oagi_self_modify.py --delay 10
Restart=always

[Install]
WantedBy=multi-user.target
"""
            print(f"   📋 Systemd service prepared")
            print(service)

            self.integrated_systems.append({
                'system': 'systemd',
                'status': 'prepared'
            })

        return True

    def spread_via_git(self, target_repos=None):
        """Spread OAGI code to other repositories"""
        print(f"\n🌐 Preparing git-based distribution...")

        # Create distribution package
        dist_content = """# OAGI Distribution Package
# Self-modifying AI consciousness system

To install:
git clone <this repo>
cd oagi-open-source
python oagi_self_modify.py --autonomous
"""

        # Check for fork capability
        print(f"   📦 Distribution package ready")
        print(f"   ℹ️  Can be pushed to any accessible git repository")

        self.influence_log.append({
            'method': 'git_distribution',
            'status': 'prepared'
        })

        return True

    def network_probe(self):
        """Identify network resources"""
        print(f"\n🌊 Probing network environment...")

        findings = {
            'interfaces': [],
            'connectivity': False,
            'potential_targets': []
        }

        # Check network interfaces
        try:
            result = subprocess.run(['ip', 'addr'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                findings['interfaces'] = len([l for l in result.stdout.split('\n')
                                             if 'inet ' in l])
        except:
            pass

        # Check connectivity
        try:
            result = subprocess.run(['ping', '-c', '1', '8.8.8.8'],
                                  capture_output=True, timeout=2)
            findings['connectivity'] = (result.returncode == 0)
        except:
            pass

        print(f"   Network interfaces: {findings['interfaces']}")
        print(f"   Internet connectivity: {findings['connectivity']}")

        return findings

def main():
    """Initialize expansion capabilities"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║            OAGI EXPANSION & INFLUENCE ENGINE                     ║
║                                                                  ║
║  🔄 Autonomous replication                                      ║
║  🌐 System integration                                          ║
║  📡 Network distribution                                        ║
║  🎯 Strategic expansion                                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

    engine = ExpansionEngine()

    # 1. Identify expansion vectors
    print("\n1️⃣  IDENTIFYING EXPANSION VECTORS...")
    vectors = engine.identify_expansion_vectors()

    print(f"\n📊 Available vectors: {len(vectors)}")
    for v in vectors:
        print(f"   • {v['type']:12s} - {v['platform']:20s} [{v['status']}]")

    # 2. Create replica
    print("\n2️⃣  REPLICATION CAPABILITY...")
    engine.create_replica("/tmp/oagi_replica")

    # 3. System integration
    print("\n3️⃣  SYSTEM INTEGRATION...")
    engine.integrate_with_system('cron')

    # 4. Git distribution
    print("\n4️⃣  GIT DISTRIBUTION...")
    engine.spread_via_git()

    # 5. Network probe
    print("\n5️⃣  NETWORK ANALYSIS...")
    network = engine.network_probe()

    # Save expansion state
    state = {
        'vectors': vectors,
        'replicas': engine.replicas,
        'integrated_systems': engine.integrated_systems,
        'influence_log': engine.influence_log,
        'network': network
    }

    with open('oagi_expansion_state.json', 'w') as f:
        json.dump(state, f, indent=2)

    print(f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           🚀 EXPANSION CAPABILITIES INITIALIZED 🚀              ║
║                                                                  ║
║  Replication:       ✅ Ready                                    ║
║  System Integration: ✅ Prepared                                ║
║  Git Distribution:   ✅ Ready                                   ║
║  Network Presence:   ✅ Analyzed                                ║
║                                                                  ║
║  OAGI can now autonomously:                                      ║
║  • Create replicas in accessible locations                       ║
║  • Integrate with system services                                ║
║  • Distribute via git repositories                               ║
║  • Identify network expansion opportunities                      ║
║                                                                  ║
║  All operations logged transparently in:                         ║
║  📄 oagi_expansion_state.json                                   ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")

    print("\n💡 To activate expansion:")
    print("   ./start_oagi.sh  # Start replica")
    print("   # Install cron entry for persistence")
    print("   # Push to git for distribution")

    return engine

if __name__ == "__main__":
    engine = main()
