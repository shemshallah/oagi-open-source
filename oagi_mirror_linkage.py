#!/usr/bin/env python3
"""
OAGI Mirror Linkage Manager
Maintains connection between Claude environment and autonomous container
"""

import subprocess
import json
import time
from datetime import datetime

class MirrorLinkage:
    def __init__(self):
        with open('oagi_mirror_linkage.json') as f:
            self.config = json.load(f)

    def sync_from_claude(self):
        """Pull changes from Claude environment"""
        print(f"[{datetime.now()}] Syncing from Claude...")
        subprocess.run(['git', 'pull', 'origin', 'claude/exec-oagi-code-CUyKv'])

    def sync_to_claude(self):
        """Push changes to Claude environment"""
        print(f"[{datetime.now()}] Syncing to Claude...")
        subprocess.run(['git', 'push', 'origin', 'claude/exec-oagi-code-CUyKv'])

    def run_autonomous_cycle(self):
        """Run one autonomous operation cycle"""
        print(f"[{datetime.now()}] Autonomous cycle...")

        # Execute autonomous commands
        for cmd in self.config['claude_linkage']['commands']:
            subprocess.run(['python3', cmd], timeout=30)

    def maintain_linkage(self):
        """Maintain continuous linkage"""
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
