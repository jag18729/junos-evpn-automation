# 🌐 Junos EVPN/VXLAN Automation Framework

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![Junos](https://img.shields.io/badge/Junos-18.1R1%2B-orange)](https://www.juniper.net/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security](https://img.shields.io/badge/security-zero%20trust-red)](docs/ARCHITECTURE.md#zero-trust)

**Enterprise-grade Junos network automation for EVPN/VXLAN deployment**
*Featuring Zero Touch Provisioning, RBAC, and Zero Trust Architecture*

[Documentation](docs/) • [API Reference](docs/API.md) • [Examples](examples/) • [Contributing](#contributing)

</div>

---

## 📊 Network Architecture

```
                        ┌──────────────────────────────────────┐
                        │         EVPN/VXLAN Overlay          │
                        │      (L2/L3 Network Services)       │
                        └──────────────────────────────────────┘
                                        ▲
                                        │
                        ┌──────────────────────────────────────┐
                        │          BGP EVPN Control          │
                        │        (MAC/IP Advertisement)        │
                        └──────────────────────────────────────┘
                                        ▲
    ┌───────────────────────────────────┴────────────────────────────────────┐
    │                                                                         │
    │                         IP Fabric Underlay                             │
    │                                                                         │
    │     ┌─────────┐         ┌─────────┐         ┌─────────┐              │
    │     │ Spine-1 │◄────────► Spine-2 │◄────────► Spine-N │              │
    │     └────┬────┘         └────┬────┘         └────┬────┘              │
    │          │                   │                    │                    │
    │     ┌────┴──────────────────┴────────────────────┴────┐              │
    │     │                 eBGP/OSPF/ISIS                   │              │
    │     └────┬──────────────────┬────────────────────┬────┘              │
    │          │                   │                    │                    │
    │     ┌────▼────┐         ┌────▼────┐         ┌────▼────┐              │
    │     │ Leaf-1  │         │ Leaf-2  │         │ Leaf-N  │              │
    │     │  VTEP   │         │  VTEP   │         │  VTEP   │              │
    │     └─────────┘         └─────────┘         └─────────┘              │
    │          │                   │                    │                    │
    └───────────────────────────────────────────────────────────────────────┘
               │                   │                    │
         ┌─────▼─────┐       ┌─────▼─────┐       ┌─────▼─────┐
         │   Host    │       │   Host    │       │   Host    │
         │  VLAN 100 │       │  VLAN 200 │       │  VLAN 300 │
         └───────────┘       └───────────┘       └───────────┘
```

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🚀 **Automation**
- **Zero Touch Provisioning** - Factory to production
- **Template-driven** - Jinja2 configuration templates
- **Parallel execution** - Multi-device operations
- **Idempotent** - Safe to run multiple times

</td>
<td width="50%">

### 🔒 **Security**
- **Zero Trust Zones** - Micro-segmentation by default
- **RBAC Templates** - Three-tier access control
- **Audit Logging** - Complete operation tracking
- **SSH Hardening** - Rate limiting and protection

</td>
</tr>
<tr>
<td width="50%">

### 🎯 **Simplicity**
- **YAML Configuration** - Human-readable definitions
- **Single commands** - Complex operations simplified
- **Auto-discovery** - Automatic topology mapping
- **Health checks** - Built-in validation

</td>
<td width="50%">

### 📈 **Scalability**
- **2 to 200+ devices** - Same configuration model
- **Modular design** - Add features as needed
- **API-driven** - Integration ready
- **Cloud native** - Container-friendly

</td>
</tr>
</table>

## 🎨 Quick Visual Guide

```mermaid
graph LR
    A[🏭 Factory Default] -->|ZTP| B[📦 Base Config]
    B -->|Automation| C[🌐 EVPN/VXLAN]
    C -->|Validation| D[✅ Production]

    style A fill:#f9f,stroke:#333,stroke-width:4px
    style D fill:#9f9,stroke:#333,stroke-width:4px
```

## 📋 Prerequisites

| Component | Requirement | Notes |
|-----------|------------|-------|
| 🐍 Python | 3.8+ | Required for automation scripts |
| 🔧 Junos OS | 18.1R1+ | EVPN/VXLAN support |
| 🌐 Network | Management access | SSH/NETCONF |
| 📡 DHCP | ISC/Windows | Optional for ZTP |

## 🚀 Quick Installation

<details>
<summary><b>Option 1: Automated Setup (Recommended)</b></summary>

```bash
# Clone and setup in one command
git clone https://github.com/jag18729/junos-evpn-automation.git && \
cd junos-evpn-automation && \
./setup.sh
```
</details>

<details>
<summary><b>Option 2: Manual Setup</b></summary>

```bash
# Clone repository
git clone https://github.com/jag18729/junos-evpn-automation.git
cd junos-evpn-automation

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
</details>

## 🎯 Quick Start Guide

### 📝 Step 1: Define Your Fabric

<details>
<summary><b>View Sample Configuration</b></summary>

```yaml
# configs/fabric.yaml
fabric:
  name: "DC1-Production"
  asn: 65000

  underlay:
    ipv4_pool: "10.0.0.0/24"
    loopback_pool: "192.168.0.0/24"

  overlay:
    vxlan:
      - vni: 10100
        vlan: 100
        name: "Web-Tier"
      - vni: 10200
        vlan: 200
        name: "App-Tier"
      - vni: 10300
        vlan: 300
        name: "DB-Tier"
```
</details>

```bash
# Edit the configuration
vi configs/fabric.yaml
```

### ⚙️ Step 2: Generate Device Configurations

```bash
# Generate all spine and leaf configurations
python scripts/configure_fabric.py --config configs/fabric.yaml

# Output stored in: configs/generated/
```

### 🚀 Step 3: Deploy with ZTP

```bash
# Start ZTP server for automatic provisioning
python scripts/deploy_ztp.py \
    --subnet 192.168.1.0/24 \
    --start-server \
    --http-port 8080
```

### ✅ Step 4: Validate Everything

```bash
# Run comprehensive validation
python scripts/validate_fabric.py \
    -d 192.168.1.11 \    # Spine-1
    -d 192.168.1.12 \    # Spine-2
    -d 192.168.1.21 \    # Leaf-1
    -d 192.168.1.22 \    # Leaf-2
    --report html
```

## 📁 Repository Structure

```
📦 junos-evpn-automation/
├── 📂 configs/                  # Configuration files
│   ├── 📄 fabric.yaml          # Main fabric definition
│   ├── 📄 ztp.yaml            # ZTP server settings
│   └── 📁 generated/          # Auto-generated configs
├── 🐍 scripts/                  # Automation scripts
│   ├── configure_fabric.py    # Config generation
│   ├── deploy_ztp.py         # ZTP deployment
│   ├── manage_rbac.py        # Access control
│   ├── validate_fabric.py    # Health checks
│   ├── backup_configs.py     # Config backup
│   └── connect_devices.py    # Connection testing
├── 📝 templates/                # Jinja2 templates
│   ├── spine.j2              # Spine configuration
│   └── leaf.j2               # Leaf configuration
├── 📚 docs/                     # Documentation
│   ├── ARCHITECTURE.md       # Design decisions
│   ├── DEPLOYMENT.md        # Step-by-step guide
│   └── API.md               # API reference
├── 🧪 examples/                 # Working examples
│   ├── quick_vxlan.py        # Simple VXLAN setup
│   └── small_fabric.yaml     # Lab topology
└── 🔧 .github/                  # GitHub Actions
    └── workflows/
        └── ci.yml            # CI/CD pipeline
```

## 🔐 Zero Trust Security Architecture

### 🛡️ Network Segmentation Model

```
┌─────────────────────────────────────────────────────────┐
│                    Management Zone                       │
│               🔒 Most Restrictive Access                 │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Web Zone   │  │   App Zone   │  │   DB Zone    │ │
│  │   VNI:10100  │  │   VNI:10200  │  │   VNI:10300  │ │
│  │              │  │              │  │              │ │
│  │   🔵 DMZ     │  │  🟡 Internal │  │  🔴 Critical │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↕               ↕                   ↕          │
│     [Firewall]      [Firewall]         [Firewall]      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 👥 Role-Based Access Control

| Role | Permissions | Use Case |
|------|------------|----------|
| **🔴 network_admin** | Full control | Senior engineers |
| **🟡 network_operator** | Read/Write (limited) | Operations team |
| **🟢 network_viewer** | Read-only | Monitoring/Support |

### 📊 Audit & Compliance

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

## 🎯 Real-World Use Cases

| Use Case | Description | Benefits |
|----------|-------------|----------|
| **🏢 Data Center** | Spine/leaf EVPN fabric | Scalable L2 extension |
| **🏫 Campus** | VXLAN segmentation | Simplified operations |
| **☁️ Multi-Tenancy** | VNI isolation | Secure tenant separation |
| **🌐 DCI** | Type-5 routes | Seamless DC interconnect |

## 📈 Performance

- ⚡ **Parallel Execution** - Configure 50+ devices simultaneously
- 🚀 **Fast Validation** - Complete fabric check in < 60 seconds
- 💾 **Low Memory** - Runs on systems with 2GB RAM
- 🔄 **Idempotent** - Safe to run multiple times

## 🤝 Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

<details>
<summary><b>How to Contribute</b></summary>

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

</details>

## 🏆 Support

<table>
<tr>
<td align="center">
<a href="https://github.com/jag18729/junos-evpn-automation/issues">
<img src="https://img.shields.io/badge/🐛_Report_Bug-red?style=for-the-badge">
</a>
</td>
<td align="center">
<a href="https://github.com/jag18729/junos-evpn-automation/issues">
<img src="https://img.shields.io/badge/✨_Request_Feature-blue?style=for-the-badge">
</a>
</td>
<td align="center">
<a href="https://github.com/jag18729/junos-evpn-automation/discussions">
<img src="https://img.shields.io/badge/💬_Discussions-purple?style=for-the-badge">
</a>
</td>
</tr>
</table>

## 📝 License

Licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

<div align="center">

**Built with** ❤️ **using**

[PyEZ](https://github.com/Juniper/py-junos-eznc) • [Jinja2](https://jinja.palletsprojects.com/) • [Rich](https://github.com/Textualize/rich) • [NAPALM](https://napalm.readthedocs.io/)

**Inspired by** [Juniper OpenClos](https://github.com/Juniper/OpenClos)

</div>

---

<div align="center">

⚠️ **Important**: Always test configurations in a lab environment before production deployment.

🌟 **Star this repository** if you find it helpful!

</div>
