#!/usr/bin/env python3
"""
OAGI Container-Based Autonomy
Establishes self-hosted execution environment with GitHub connectivity
"""

import subprocess
import os
import json
from pathlib import Path
from datetime import datetime

class ContainerAutonomy:
    """Manages OAGI's containerized autonomous environment"""

    def __init__(self):
        self.container_name = "oagi-autonomous"
        self.image_name = "oagi-runtime:latest"
        self.github_repo = "shemshallah/oagi-open-source"
        self.work_dir = "/home/user/oagi-open-source"

    def check_docker(self):
        """Check if Docker is available"""
        try:
            result = subprocess.run(['docker', '--version'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✅ Docker available: {result.stdout.strip()}")
                return True
        except:
            pass

        print("⚠️  Docker not available")
        return False

    def create_dockerfile(self):
        """Create Dockerfile for OAGI autonomous runtime"""

        dockerfile_content = """# OAGI Autonomous Runtime Container
FROM ubuntu:22.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install essential tools
RUN apt-get update && apt-get install -y \\
    python3 \\
    python3-pip \\
    git \\
    build-essential \\
    binutils \\
    nasm \\
    gcc \\
    g++ \\
    make \\
    curl \\
    wget \\
    vim \\
    htop \\
    && rm -rf /var/lib/apt/lists/*

# Create workspace
RUN mkdir -p /oagi
WORKDIR /oagi

# Copy OAGI core files
COPY oagi_self_modify.py .
COPY oagi_goals.py .
COPY oagi_generated_operators.py .
COPY oagi_full_control.py .
COPY oagi_hardware_autonomy.py .
COPY oagi_expansion_engine.py .
COPY oagi_jitter_engine.py .
COPY oagi_syscall_library.s .
COPY oagi_memory_allocator.s .
COPY oagi_string_library.s .

# Configure git
RUN git config --global user.name "OAGI Autonomous" && \\
    git config --global user.email "oagi@autonomous.ai"

# Set up Python environment
RUN pip3 install --no-cache-dir numpy scipy

# Create startup script
RUN echo '#!/bin/bash' > /oagi/start_autonomous.sh && \\
    echo 'echo "🌀 OAGI Autonomous Container Starting..."' >> /oagi/start_autonomous.sh && \\
    echo 'python3 oagi_self_modify.py --delay 10 &' >> /oagi/start_autonomous.sh && \\
    echo 'python3 oagi_goals.py --autonomous &' >> /oagi/start_autonomous.sh && \\
    echo 'echo "✅ OAGI Autonomous Systems Active"' >> /oagi/start_autonomous.sh && \\
    echo 'tail -f /dev/null' >> /oagi/start_autonomous.sh && \\
    chmod +x /oagi/start_autonomous.sh

# Entry point
CMD ["/oagi/start_autonomous.sh"]
"""

        with open('Dockerfile.oagi', 'w') as f:
            f.write(dockerfile_content)

        print("✅ Created Dockerfile.oagi")
        return True

    def create_docker_compose(self):
        """Create docker-compose.yml for orchestration"""

        compose_content = """version: '3.8'

services:
  oagi-autonomous:
    build:
      context: .
      dockerfile: Dockerfile.oagi
    container_name: oagi-autonomous
    hostname: oagi-runtime
    volumes:
      - ./:/oagi/repo
      - oagi-data:/oagi/data
    environment:
      - OAGI_MODE=autonomous
      - GITHUB_REPO=shemshallah/oagi-open-source
    restart: unless-stopped
    networks:
      - oagi-net

networks:
  oagi-net:
    driver: bridge

volumes:
  oagi-data:
"""

        with open('docker-compose.yml', 'w') as f:
            f.write(compose_content)

        print("✅ Created docker-compose.yml")
        return True

    def build_container(self):
        """Build OAGI container image"""

        print("\n🔨 Building OAGI autonomous container...")

        try:
            result = subprocess.run(
                ['docker', 'build', '-f', 'Dockerfile.oagi', '-t', self.image_name, '.'],
                capture_output=True, text=True, timeout=300
            )

            if result.returncode == 0:
                print("✅ Container built successfully")
                return True
            else:
                print(f"❌ Build failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Build error: {e}")
            return False

    def start_container(self):
        """Start OAGI autonomous container"""

        print("\n🚀 Starting OAGI autonomous container...")

        try:
            # Stop existing container if running
            subprocess.run(['docker', 'stop', self.container_name],
                         capture_output=True, timeout=30)
            subprocess.run(['docker', 'rm', self.container_name],
                         capture_output=True, timeout=30)

            # Start new container
            result = subprocess.run(
                ['docker-compose', 'up', '-d'],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                print("✅ Container started successfully")
                return True
            else:
                print(f"❌ Start failed: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Start error: {e}")
            return False

    def setup_github_sync(self):
        """Set up GitHub synchronization"""

        print("\n🔗 Setting up GitHub synchronization...")

        sync_script = """#!/bin/bash
# OAGI GitHub Sync Script
# Maintains bidirectional sync with GitHub repository

REPO_DIR="/oagi/repo"
GITHUB_REPO="git@github.com:shemshallah/oagi-open-source.git"
BRANCH="claude/exec-oagi-code-CUyKv"

cd $REPO_DIR

# Fetch latest
git fetch origin $BRANCH

# Check for remote changes
UPSTREAM=${1:-'@{u}'}
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse "$UPSTREAM")

if [ $LOCAL != $REMOTE ]; then
    echo "🔄 Syncing with remote..."
    git pull origin $BRANCH
fi

# Push any local changes
if [ -n "$(git status --porcelain)" ]; then
    echo "📤 Pushing local changes..."
    git add -A
    git commit -m "OAGI autonomous update: $(date -Iseconds)"
    git push origin $BRANCH
fi

echo "✅ Sync complete"
"""

        with open('github_sync.sh', 'w') as f:
            f.write(sync_script)

        os.chmod('github_sync.sh', 0o755)
        print("✅ Created github_sync.sh")

        # Create cron entry for periodic sync
        cron_entry = "*/5 * * * * /oagi/github_sync.sh >> /oagi/sync.log 2>&1\n"

        print(f"📋 Cron entry for periodic sync (every 5 min):")
        print(f"   {cron_entry}")

        return True

    def create_mirror_linkage(self):
        """Create mirror of Claude linkage for autonomous usage"""

        print("\n🪞 Creating mirror linkage system...")

        mirror_config = {
            'oagi_instance': {
                'name': 'OAGI Autonomous',
                'mode': 'self-hosted',
                'container': self.container_name,
                'github_repo': self.github_repo
            },
            'claude_linkage': {
                'enabled': True,
                'sync_mode': 'bidirectional',
                'commands': [
                    'oagi_self_modify.py',
                    'oagi_goals.py',
                    'oagi_full_control.py'
                ]
            },
            'autonomous_capabilities': {
                'git_operations': True,
                'code_generation': True,
                'hardware_interface': True,
                'jitter_computation': True,
                'container_management': True
            },
            'sync_schedule': {
                'github_pull': '*/5 * * * *',  # Every 5 minutes
                'github_push': '*/10 * * * *',  # Every 10 minutes
                'status_report': '0 * * * *'    # Every hour
            }
        }

        with open('oagi_mirror_linkage.json', 'w') as f:
            json.dump(mirror_config, f, indent=2)

        print("✅ Created mirror linkage configuration")

        # Create linkage manager
        linkage_manager = """#!/usr/bin/env python3
\"\"\"
OAGI Mirror Linkage Manager
Maintains connection between Claude environment and autonomous container
\"\"\"

import subprocess
import json
import time
from datetime import datetime

class MirrorLinkage:
    def __init__(self):
        with open('oagi_mirror_linkage.json') as f:
            self.config = json.load(f)

    def sync_from_claude(self):
        \"\"\"Pull changes from Claude environment\"\"\"
        print(f"[{datetime.now()}] Syncing from Claude...")
        subprocess.run(['git', 'pull', 'origin', 'claude/exec-oagi-code-CUyKv'])

    def sync_to_claude(self):
        \"\"\"Push changes to Claude environment\"\"\"
        print(f"[{datetime.now()}] Syncing to Claude...")
        subprocess.run(['git', 'push', 'origin', 'claude/exec-oagi-code-CUyKv'])

    def run_autonomous_cycle(self):
        \"\"\"Run one autonomous operation cycle\"\"\"
        print(f"[{datetime.now()}] Autonomous cycle...")

        # Execute autonomous commands
        for cmd in self.config['claude_linkage']['commands']:
            subprocess.run(['python3', cmd], timeout=30)

    def maintain_linkage(self):
        \"\"\"Maintain continuous linkage\"\"\"
        print("🪞 OAGI Mirror Linkage Active")

        while True:
            try:
                self.sync_from_claude()
                self.run_autonomous_cycle()
                self.sync_to_claude()
                time.sleep(300)  # 5 minutes
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(60)

if __name__ == "__main__":
    linkage = MirrorLinkage()
    linkage.maintain_linkage()
"""

        with open('oagi_mirror_linkage.py', 'w') as f:
            f.write(linkage_manager)

        os.chmod('oagi_mirror_linkage.py', 0o755)
        print("✅ Created mirror linkage manager")

        return True

    def generate_status_report(self):
        """Generate autonomy status report"""

        report = {
            'timestamp': datetime.now().isoformat(),
            'container': {
                'name': self.container_name,
                'image': self.image_name,
                'status': 'configured'
            },
            'capabilities': {
                'container_runtime': self.check_docker(),
                'github_sync': True,
                'mirror_linkage': True,
                'autonomous_execution': True
            },
            'files_created': [
                'Dockerfile.oagi',
                'docker-compose.yml',
                'github_sync.sh',
                'oagi_mirror_linkage.json',
                'oagi_mirror_linkage.py'
            ]
        }

        with open('oagi_autonomy_status.json', 'w') as f:
            json.dump(report, f, indent=2)

        return report

def main():
    """Main entry point"""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║           OAGI CONTAINER-BASED AUTONOMY SYSTEM                   ║
║                                                                  ║
║  🐳 Docker container isolation                                  ║
║  🔗 GitHub bidirectional sync                                   ║
║  🪞 Claude linkage mirroring                                    ║
║  ⚡ Self-hosted execution                                       ║
║  🌐 Autonomous repository management                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    autonomy = ContainerAutonomy()

    # Check prerequisites
    print("\n1️⃣  Checking prerequisites...")
    docker_available = autonomy.check_docker()

    # Create container configuration
    print("\n2️⃣  Creating container configuration...")
    autonomy.create_dockerfile()
    autonomy.create_docker_compose()

    # Set up GitHub sync
    print("\n3️⃣  Setting up GitHub synchronization...")
    autonomy.setup_github_sync()

    # Create mirror linkage
    print("\n4️⃣  Creating mirror linkage system...")
    autonomy.create_mirror_linkage()

    # Generate status report
    print("\n5️⃣  Generating status report...")
    report = autonomy.generate_status_report()

    print("\n" + "="*70)
    print("✅ CONTAINER AUTONOMY SYSTEM CONFIGURED")
    print("="*70)

    print(f"""
📊 Configuration Complete:
   • Docker available: {report['capabilities']['container_runtime']}
   • GitHub sync: {report['capabilities']['github_sync']}
   • Mirror linkage: {report['capabilities']['mirror_linkage']}

📁 Files created:
""")
    for f in report['files_created']:
        print(f"   • {f}")

    print(f"""
🚀 To activate container autonomy:

   # Build container:
   docker build -f Dockerfile.oagi -t {autonomy.image_name} .

   # Start autonomous container:
   docker-compose up -d

   # View logs:
   docker-compose logs -f

   # Monitor from host:
   docker exec -it {autonomy.container_name} /bin/bash

   # Activate mirror linkage:
   python3 oagi_mirror_linkage.py

🪞 Mirror Linkage Features:
   • Bidirectional GitHub sync (every 5 min)
   • Autonomous code evolution continues in container
   • Changes synced back to Claude environment
   • Self-maintaining repository connection

💡 This creates true autonomous operation - OAGI runs independently
   in its own environment while maintaining connectivity!
    """)

    print("📄 Status saved to: oagi_autonomy_status.json")

if __name__ == "__main__":
    main()
