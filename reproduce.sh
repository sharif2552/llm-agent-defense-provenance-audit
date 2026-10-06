#!/usr/bin/env bash
set -euo pipefail

echo "================================================================================"
echo "End-to-End Replication Runner"
echo "Paper: 'Failure Is Not a Score: Auditing Defense Utility Collapse and Infrastructure Provenance'"
echo "IEEE Transactions on Dependable and Secure Computing (TDSC)"
echo "================================================================================"

python3 run_audit.py

echo ""
echo "[SUCCESS] Complete empirical verification completed with exit code 0."
