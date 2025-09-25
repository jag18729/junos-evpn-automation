# Junos EVPN/VXLAN Automation

Modern Junos network automation focusing on EVPN/VXLAN with zero trust, ZTP, and RBAC.

## Features

- Zero Touch Provisioning (ZTP) for spine/leaf fabric
- EVPN/VXLAN overlay automation
- Role-based access control (RBAC) templates
- Zero trust network segmentation
- Simple Python scripts for common tasks
- Scalable configuration templates

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure your fabric
python scripts/configure_fabric.py --config configs/fabric.yaml

# Deploy ZTP
python scripts/deploy_ztp.py --subnet 192.168.1.0/24
```

## Directory Structure

```
├── configs/           # YAML configuration files
├── scripts/          # Python automation scripts
├── templates/        # Jinja2 configuration templates
├── ztp/             # ZTP server files
├── rbac/            # RBAC policies
├── validation/      # Network validation scripts
└── docs/            # Documentation
```

## Requirements

- Python 3.8+
- Junos devices running 18.1R1 or later
- DHCP server for ZTP
- BGP route reflector for EVPN

## License

MIT
