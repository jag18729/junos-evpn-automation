# Junos EVPN/VXLAN Automation

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Junos](https://img.shields.io/badge/Junos-18.1R1%2B-orange)](https://www.juniper.net/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Modern Junos network automation framework for EVPN/VXLAN deployment with zero trust security, ZTP, and RBAC.

## 🚀 Features

- **Zero Touch Provisioning (ZTP)** - Automated device provisioning from factory default
- **EVPN/VXLAN Automation** - Complete overlay network configuration
- **Role-Based Access Control** - Pre-built RBAC templates with three-tier access
- **Zero Trust Segmentation** - Network micro-segmentation by default
- **Validation Tools** - Automated fabric health checks and reporting
- **Simple & Scalable** - YAML-driven configuration for any size deployment

## 📋 Prerequisites

- Python 3.8 or higher
- Junos devices running 18.1R1 or later
- Network access to devices
- DHCP server for ZTP (optional)

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/jag18729/junos-evpn-automation.git
cd junos-evpn-automation

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

## 📚 Quick Start

### 1. Configure Your Fabric

Edit `configs/fabric.yaml` with your network details:

```yaml
fabric:
  name: "DC1"
  asn: 65000
  underlay:
    ipv4_pool: "10.0.0.0/24"
    loopback_pool: "192.168.0.0/24"
```

### 2. Generate Configurations

```bash
python scripts/configure_fabric.py --config configs/fabric.yaml
```

### 3. Deploy ZTP Server

```bash
python scripts/deploy_ztp.py --subnet 192.168.1.0/24 --start-server
```

### 4. Validate Deployment

```bash
python scripts/validate_fabric.py -d 192.168.1.11 -d 192.168.1.21 -u admin
```

## 📁 Project Structure

```
junos-evpn-automation/
├── configs/              # YAML configuration files
│   ├── fabric.yaml      # Main fabric configuration
│   └── ztp.yaml         # ZTP server settings
├── scripts/             # Python automation scripts
│   ├── configure_fabric.py    # Generate device configs
│   ├── deploy_ztp.py          # ZTP server deployment
│   ├── manage_rbac.py         # RBAC configuration
│   ├── validate_fabric.py     # Fabric validation
│   └── connect_devices.py     # Simple connection tool
├── templates/           # Jinja2 configuration templates
│   ├── spine.j2        # Spine switch template
│   └── leaf.j2         # Leaf switch template
├── ztp/                # ZTP server files
├── rbac/               # RBAC policies
└── validation/         # Validation reports
```

## 🔐 Security Features

### Zero Trust Network Segmentation

- Automatic zone isolation
- Micro-segmentation policies
- Cross-zone traffic logging

### RBAC Implementation

Three built-in roles:
- **network_admin** - Full access
- **network_operator** - Operational access
- **network_viewer** - Read-only access

### Audit & Compliance

- Comprehensive logging
- Command accounting
- SSH rate limiting
- Failed login tracking

## 🛠️ Script Usage

### configure_fabric.py

Generates complete spine/leaf configurations:

```bash
python scripts/configure_fabric.py --config configs/fabric.yaml --dry-run
```

Options:
- `--config` - Fabric configuration file
- `--output` - Output directory for configs
- `--dry-run` - Preview without saving

### deploy_ztp.py

Sets up ZTP server for automated provisioning:

```bash
python scripts/deploy_ztp.py --subnet 192.168.1.0/24 --config configs/fabric.yaml
```

Options:
- `--subnet` - Management network subnet
- `--config` - Fabric configuration file
- `--start-server` - Launch HTTP server

### manage_rbac.py

Configure role-based access control:

```bash
python scripts/manage_rbac.py --action create --username john --role network_operator
```

Options:
- `--action` - create, deploy, or template
- `--username` - Username to create
- `--role` - RBAC role to assign
- `--device` - Target device IP

### validate_fabric.py

Comprehensive fabric validation:

```bash
python scripts/validate_fabric.py -d 192.168.1.11 -d 192.168.1.21 -u admin --report report.txt
```

Options:
- `-d, --devices` - Device IPs to validate (multiple)
- `-u, --username` - Device username
- `--report` - Output report file

## 📊 Validation Checks

The validation tool performs:
- BGP neighbor status
- EVPN database verification
- VXLAN VTEP status
- Interface status
- End-to-end connectivity

## 🎯 Use Cases

- **Data Center Fabric** - Build spine/leaf EVPN/VXLAN fabric
- **Campus Networks** - Deploy VXLAN for campus segmentation
- **Multi-Tenancy** - Isolate tenant networks with VNIs
- **DCI** - Data center interconnect with EVPN Type-5 routes

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Inspired by Juniper's OpenClos project
- Built with PyEZ and Jinja2
- Uses Rich for terminal output

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This is a framework for automation. Always test configurations in a lab environment before deploying to production.
