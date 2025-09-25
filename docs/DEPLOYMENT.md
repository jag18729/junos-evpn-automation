# 🚀 Deployment Guide

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Initial Setup](#initial-setup)
- [Fabric Deployment](#fabric-deployment)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)
- [Production Checklist](#production-checklist)

## Prerequisites

### System Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| **CPU** | 2 cores | 4+ cores | For parallel operations |
| **RAM** | 2 GB | 4+ GB | Depends on fabric size |
| **Disk** | 10 GB | 20+ GB | For logs and backups |
| **Python** | 3.8 | 3.10+ | Latest stable version |
| **OS** | Linux/macOS | Ubuntu 20.04+ | Windows via WSL2 |

### Network Requirements

```
✅ Management network connectivity to all devices
✅ SSH access enabled on Junos devices
✅ NETCONF over SSH (port 830) enabled
✅ DNS resolution for device hostnames (optional)
✅ NTP synchronized across all devices
```

### Junos Prerequisites

```junos
# Enable NETCONF
set system services netconf ssh

# Enable SSH
set system services ssh root-login allow
set system services ssh protocol-version v2

# Set authentication
set system login user automation class super-user
set system login user automation authentication ssh-rsa "ssh-rsa AAAAB3..."
```

## Installation

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/jag18729/junos-evpn-automation.git
cd junos-evpn-automation
```

### Step 2: Setup Python Environment

```bash
# Run automated setup
./setup.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Verify Installation

```bash
# Check Python version
python --version

# Verify dependencies
pip list | grep -E "junos-eznc|jinja2|pyyaml|rich"

# Test connectivity tool
python scripts/connect_devices.py --help
```

## Initial Setup

### 1️⃣ Configure Fabric Definition

Create your fabric configuration file:

```yaml
# configs/fabric.yaml
fabric:
  name: "DC1-Production"
  description: "Primary Data Center Fabric"

  # Global Settings
  global:
    asn: 65000
    router_id_start: "192.168.0.1"
    vrf_target: "target:65000:1"

  # Underlay Configuration
  underlay:
    protocol: "ebgp"  # Options: ebgp, ospf, isis
    ipv4_pool: "10.0.0.0/24"
    ipv6_pool: "2001:db8::/32"
    loopback_pool: "192.168.0.0/24"
    bfd: true

  # Overlay Configuration
  overlay:
    evpn_model: "vlan-based"  # Options: vlan-based, vlan-aware
    replication: "ingress"     # Options: ingress, multicast

  # Spine Switches
  spines:
    - name: "spine-01"
      management_ip: "192.168.1.11"
      asn: 65001

    - name: "spine-02"
      management_ip: "192.168.1.12"
      asn: 65002

  # Leaf Switches
  leafs:
    - name: "leaf-01"
      management_ip: "192.168.1.21"
      asn: 65011
      rack: 1

    - name: "leaf-02"
      management_ip: "192.168.1.22"
      asn: 65012
      rack: 1

  # VNI Definitions
  vnis:
    - vni: 10100
      vlan: 100
      name: "Web-Tier"
      subnet: "172.16.100.0/24"
      gateway: "172.16.100.1"

    - vni: 10200
      vlan: 200
      name: "App-Tier"
      subnet: "172.16.200.0/24"
      gateway: "172.16.200.1"
```

### 2️⃣ Configure ZTP Settings

```yaml
# configs/ztp.yaml
ztp:
  server:
    ip: "192.168.1.10"
    http_port: 8080
    tftp_port: 69

  dhcp:
    subnet: "192.168.1.0/24"
    range_start: "192.168.1.100"
    range_end: "192.168.1.200"
    gateway: "192.168.1.1"
    dns: ["8.8.8.8", "8.8.4.4"]

  options:
    vendor_class: "Juniper"
    config_file: "juniper.conf"
    software_image: "junos-21.4R3.12.tgz"
```

### 3️⃣ Set Environment Variables

```bash
# Create .env file
cat > .env << EOF
JUNOS_USERNAME=automation
JUNOS_PASSWORD=SecurePass123!
JUNOS_TIMEOUT=30
LOG_LEVEL=INFO
PARALLEL_WORKERS=10
EOF

# Load environment
source .env
```

## Fabric Deployment

### Phase 1: Generate Configurations

```bash
# Generate all device configurations
python scripts/configure_fabric.py \
    --config configs/fabric.yaml \
    --output configs/generated/

# Preview generated configs
ls -la configs/generated/
cat configs/generated/spine-01.conf
```

### Phase 2: Deploy ZTP Server

```bash
# Start ZTP server
python scripts/deploy_ztp.py \
    --config configs/ztp.yaml \
    --fabric configs/fabric.yaml \
    --start-server

# Verify ZTP server status
curl http://192.168.1.10:8080/status
```

### Phase 3: Configure Devices

```bash
# Deploy to all devices
python scripts/configure_fabric.py \
    --config configs/fabric.yaml \
    --deploy \
    --parallel

# Or deploy to specific devices
python scripts/configure_fabric.py \
    --config configs/fabric.yaml \
    --deploy \
    --devices spine-01,leaf-01
```

### Phase 4: Configure RBAC

```bash
# Deploy RBAC configuration
python scripts/manage_rbac.py \
    --action deploy \
    --config configs/rbac.yaml \
    --devices all

# Create specific users
python scripts/manage_rbac.py \
    --action create \
    --username john.doe \
    --role network_operator \
    --devices spine-01
```

## Validation

### 🔍 Comprehensive Validation

```bash
# Full fabric validation
python scripts/validate_fabric.py \
    --config configs/fabric.yaml \
    --all-devices \
    --report-format html \
    --output validation_report.html
```

### Validation Checklist

```
✓ Underlay Connectivity
  □ All spine-leaf links up
  □ BGP/OSPF/ISIS neighbors established
  □ Loopback reachability

✓ Overlay Services
  □ EVPN BGP sessions established
  □ VTEP discovery successful
  □ VNI to VLAN mappings correct

✓ End-to-End Testing
  □ MAC learning operational
  □ ARP resolution working
  □ Inter-VNI routing functional

✓ Redundancy
  □ Multi-homing operational
  □ BFD sessions active
  □ Load balancing verified
```

### Sample Validation Output

```
┌─────────────────────────────────────────────┐
│         Fabric Validation Report             │
├─────────────────────────────────────────────┤
│                                              │
│ Device: spine-01                   ✅ PASS   │
│ ├─ Management Connection:          ✅        │
│ ├─ BGP Neighbors:                  ✅ 4/4    │
│ ├─ Interface Status:               ✅ 10/10  │
│ └─ Configuration Compliance:       ✅ 100%   │
│                                              │
│ Device: leaf-01                    ✅ PASS   │
│ ├─ Management Connection:          ✅        │
│ ├─ EVPN Database:                  ✅ 25     │
│ ├─ VXLAN VTEPs:                    ✅ 3      │
│ └─ VNI Mappings:                   ✅ 5/5    │
│                                              │
│ Overall Status: ✅ HEALTHY                   │
│ Total Devices: 8/8                          │
│ Test Duration: 23.5 seconds                 │
│                                              │
└─────────────────────────────────────────────┘
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: BGP Sessions Not Establishing

```bash
# Check BGP configuration
show bgp summary
show bgp neighbor 10.0.0.1

# Verify connectivity
ping 10.0.0.1 source 192.168.0.1
traceroute 10.0.0.1

# Check firewall rules
show security policies
```

#### Issue: VXLAN Tunnel Not Forming

```bash
# Verify VTEP configuration
show ethernet-switching vxlan-tunnel-end-point source
show ethernet-switching vxlan-tunnel-end-point remote

# Check VNI mappings
show vlans extensive

# Verify multicast (if using multicast replication)
show pim neighbors
```

#### Issue: No MAC Learning

```bash
# Check EVPN database
show evpn database
show evpn mac-table

# Verify EVPN instance
show evpn instance extensive

# Check route installation
show route table bgp.evpn.0
```

### Debug Commands

```bash
# Enable debugging (use with caution)
python scripts/validate_fabric.py --debug --verbose

# Collect diagnostic bundle
python scripts/collect_diagnostics.py \
    --devices all \
    --output diag_bundle.tar.gz

# Real-time monitoring
python scripts/monitor_fabric.py \
    --interval 5 \
    --metrics bgp,vxlan,interface
```

## Production Checklist

### Pre-Deployment

- [ ] Lab testing completed
- [ ] Change window scheduled
- [ ] Rollback plan documented
- [ ] Backup configurations saved
- [ ] Team notifications sent

### Deployment

- [ ] Pre-checks executed
- [ ] Configurations deployed
- [ ] Validation tests passed
- [ ] Monitoring verified
- [ ] Documentation updated

### Post-Deployment

- [ ] Performance metrics collected
- [ ] Incident reports closed
- [ ] Lessons learned documented
- [ ] Automation scripts updated
- [ ] Knowledge base updated

## Advanced Deployment Scenarios

### Multi-Site Deployment

```yaml
# configs/multi-site.yaml
sites:
  dc1:
    fabric_config: "configs/dc1-fabric.yaml"
    management_subnet: "192.168.1.0/24"
    asn_range: "65001-65099"

  dc2:
    fabric_config: "configs/dc2-fabric.yaml"
    management_subnet: "192.168.2.0/24"
    asn_range: "65101-65199"

dci:
  enabled: true
  protocol: "evpn-type5"
  wan_links:
    - dc1_device: "border-leaf-01"
      dc2_device: "border-leaf-01"
      subnet: "10.255.0.0/31"
```

### Gradual Migration

```python
# scripts/gradual_migration.py
def migrate_rack(rack_id):
    """Migrate one rack at a time"""

    # Step 1: Prepare new leaf switches
    prepare_new_leafs(rack_id)

    # Step 2: Establish parallel infrastructure
    configure_parallel_links(rack_id)

    # Step 3: Migrate workloads
    migrate_vms(rack_id)

    # Step 4: Decommission old switches
    decommission_legacy(rack_id)
```

### Integration with CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - test
  - deploy

validate_configs:
  stage: validate
  script:
    - python scripts/validate_configs.py

test_deployment:
  stage: test
  script:
    - python scripts/test_deployment.py --environment lab

production_deploy:
  stage: deploy
  script:
    - python scripts/configure_fabric.py --deploy --production
  only:
    - main
  when: manual
```

## Monitoring and Maintenance

### Health Check Automation

```bash
# Schedule regular health checks
crontab -e
0 */4 * * * /opt/junos-automation/scripts/validate_fabric.py --quiet

# Set up alerting
python scripts/setup_alerting.py \
    --webhook https://hooks.slack.com/services/xxx \
    --email ops-team@company.com
```

### Capacity Planning

```python
# Monitor utilization trends
python scripts/capacity_report.py \
    --period 30d \
    --threshold 80 \
    --predict 90d
```

---

[Back to Main Documentation](../README.md) | [Architecture Guide](ARCHITECTURE.md) | [API Reference](API.md)