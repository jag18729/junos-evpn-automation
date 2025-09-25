#!/bin/bash
# Setup script for Junos EVPN/VXLAN Automation

echo "Setting up Junos EVPN/VXLAN Automation environment..."

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
mkdir -p configs/generated
mkdir -p ztp/{configs,scripts,images}
mkdir -p validation/reports
mkdir -p docs

# Set execute permissions on scripts
chmod +x scripts/*.py

echo "Setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "Quick start commands:"
echo "  python scripts/configure_fabric.py --config configs/fabric.yaml"
echo "  python scripts/deploy_ztp.py --subnet 192.168.1.0/24"
echo "  python scripts/validate_fabric.py -d 192.168.1.10 -d 192.168.1.11"
