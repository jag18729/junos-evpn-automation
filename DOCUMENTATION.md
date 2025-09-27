# 📚 Junos EVPN/VXLAN Automation - Documentation Hub

## 🏠 Quick Navigation

### Getting Started
- [README - Project Overview](README.md)
- [Setup Instructions](README.md#-installation)
- [Quick Start Guide](README.md#-quick-start)

### Core Documentation
- [**Architecture Guide**](docs/ARCHITECTURE.md) - System design and components
- [**Deployment Guide**](docs/DEPLOYMENT.md) - Step-by-step deployment instructions
- [**API Reference**](docs/API.md) - Complete API documentation

### Configuration Files
- [`configs/fabric.yaml`](configs/fabric.yaml) - Main fabric configuration
- [`configs/ztp.yaml`](configs/ztp.yaml) - ZTP server settings

### Example Files
- [`examples/quick_vxlan.py`](examples/quick_vxlan.py) - Quick VXLAN setup script
- [`examples/small_fabric.yaml`](examples/small_fabric.yaml) - Small fabric configuration

### Scripts
- **Setup & Configuration**
  - [`scripts/configure_fabric.py`](scripts/configure_fabric.py) - Main fabric configuration
  - [`scripts/deploy_ztp.py`](scripts/deploy_ztp.py) - ZTP deployment
  - [`scripts/manage_rbac.py`](scripts/manage_rbac.py) - RBAC management

- **Operations**
  - [`scripts/connect_devices.py`](scripts/connect_devices.py) - Device connectivity
  - [`scripts/validate_fabric.py`](scripts/validate_fabric.py) - Fabric validation
  - [`scripts/backup_configs.py`](scripts/backup_configs.py) - Configuration backup

### Templates
- [`templates/leaf.j2`](templates/leaf.j2) - Leaf switch template
- [`templates/spine.j2`](templates/spine.j2) - Spine switch template

## 🚀 Quick Start Workflow

### 1. Initial Setup
```bash
# Run the setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Configure Your Fabric
```bash
# Edit the fabric configuration
nano configs/fabric.yaml

# Review ZTP settings
nano configs/ztp.yaml
```

### 3. Deploy ZTP (Optional)
```bash
# Deploy ZTP server
python scripts/deploy_ztp.py
```

### 4. Configure Devices
```bash
# Connect to devices
python scripts/connect_devices.py

# Configure the fabric
python scripts/configure_fabric.py

# Setup RBAC
python scripts/manage_rbac.py
```

### 5. Validate Deployment
```bash
# Validate fabric configuration
python scripts/validate_fabric.py

# Backup configurations
python scripts/backup_configs.py
```

## 📖 Key Features

### Zero Touch Provisioning (ZTP)
- Automated device provisioning from factory defaults
- DHCP-based configuration deployment
- Automatic role detection (spine/leaf)

### EVPN/VXLAN Automation
- Complete overlay network configuration
- Automated VNI assignment
- Multi-tenancy support

### Role-Based Access Control (RBAC)
- Three-tier access model (Admin/Operator/Viewer)
- Pre-built permission templates
- Audit logging

### Zero Trust Security
- Network micro-segmentation
- Default-deny policies
- Encrypted control plane

### Validation & Monitoring
- Automated health checks
- Configuration validation
- Performance metrics

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Issues**
   - Verify network connectivity
   - Check SSH credentials
   - Confirm device is reachable

2. **Configuration Errors**
   - Validate YAML syntax
   - Check template variables
   - Review device logs

3. **ZTP Problems**
   - Verify DHCP configuration
   - Check TFTP server access
   - Review ZTP logs

## 📝 Configuration Examples

### Small Fabric (2 Spines, 4 Leafs)
```yaml
fabric:
  name: "DC1"
  asn: 65000
  spines:
    - name: "spine1"
      loopback: "10.0.0.1"
    - name: "spine2"
      loopback: "10.0.0.2"
  leafs:
    - name: "leaf1"
      loopback: "10.0.0.11"
    - name: "leaf2"
      loopback: "10.0.0.12"
```

### VXLAN Configuration
```python
# Quick VXLAN setup
from scripts.configure_fabric import FabricConfigurator

fabric = FabricConfigurator('configs/fabric.yaml')
fabric.deploy_vxlan(vni=10001, vlan=100)
```

## 📊 Project Structure
```
junos-evpn-automation/
├── configs/           # Configuration files
├── docs/             # Documentation
├── examples/         # Example configurations
├── scripts/          # Automation scripts
├── templates/        # Jinja2 templates
├── README.md         # Project overview
├── requirements.txt  # Python dependencies
└── setup.sh         # Setup script
```

## 🔗 Additional Resources

- [Juniper Networks Documentation](https://www.juniper.net/documentation/)
- [EVPN/VXLAN Best Practices](https://www.juniper.net/documentation/en_US/release-independent/solutions/topics/concept/evpn-vxlan-campus-introduction.html)
- [PyEZ Documentation](https://www.juniper.net/documentation/en_US/junos-pyez/topics/concept/junos-pyez-overview.html)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

For questions or issues:
1. Check this documentation
2. Review the [Architecture Guide](docs/ARCHITECTURE.md)
3. Consult the [API Reference](docs/API.md)
4. Open an issue on GitHub