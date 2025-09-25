# 📚 API Reference

## 📋 Table of Contents
- [Scripts Overview](#scripts-overview)
- [configure_fabric.py](#configure_fabricpy)
- [deploy_ztp.py](#deploy_ztppy)
- [manage_rbac.py](#manage_rbacpy)
- [validate_fabric.py](#validate_fabricpy)
- [backup_configs.py](#backup_configspy)
- [connect_devices.py](#connect_devicespy)
- [Template Functions](#template-functions)
- [Utility Functions](#utility-functions)

## Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `configure_fabric.py` | Generate and deploy fabric configurations | Production deployment |
| `deploy_ztp.py` | Setup ZTP server for automated provisioning | Initial deployment |
| `manage_rbac.py` | Configure role-based access control | Security setup |
| `validate_fabric.py` | Validate fabric health and compliance | Health monitoring |
| `backup_configs.py` | Backup device configurations | Disaster recovery |
| `connect_devices.py` | Test device connectivity | Troubleshooting |

## configure_fabric.py

### Description
Generates and deploys EVPN/VXLAN fabric configurations based on YAML definitions.

### Usage
```bash
python scripts/configure_fabric.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/fabric.yaml` | Path to fabric configuration file |
| `--output` | PATH | `configs/generated/` | Output directory for generated configs |
| `--deploy` | FLAG | False | Deploy configurations to devices |
| `--dry-run` | FLAG | False | Preview changes without applying |
| `--parallel` | FLAG | False | Deploy to multiple devices simultaneously |
| `--devices` | LIST | All | Specific devices to configure |
| `--rollback` | FLAG | False | Rollback to previous configuration |
| `--verbose` | FLAG | False | Enable verbose output |

### Examples

```bash
# Generate configurations only
python scripts/configure_fabric.py --config configs/fabric.yaml

# Deploy to all devices
python scripts/configure_fabric.py --config configs/fabric.yaml --deploy

# Deploy to specific devices in parallel
python scripts/configure_fabric.py \
    --config configs/fabric.yaml \
    --deploy \
    --devices spine-01,leaf-01 \
    --parallel

# Dry run to preview changes
python scripts/configure_fabric.py \
    --config configs/fabric.yaml \
    --deploy \
    --dry-run
```

### Configuration File Format

```yaml
fabric:
  name: string          # Fabric name
  asn: integer         # Base ASN
  underlay:
    protocol: string   # ebgp|ospf|isis
    ipv4_pool: cidr   # IPv4 address pool
  overlay:
    evpn_model: string # vlan-based|vlan-aware
  spines: list        # Spine switch definitions
  leafs: list         # Leaf switch definitions
  vnis: list          # VNI to VLAN mappings
```

### Python API

```python
from scripts.configure_fabric import FabricConfigurator

# Initialize configurator
config = FabricConfigurator(config_file='configs/fabric.yaml')

# Generate configurations
configs = config.generate_all()

# Deploy to devices
results = config.deploy(devices=['spine-01', 'leaf-01'])

# Validate deployment
status = config.validate()
```

## deploy_ztp.py

### Description
Sets up and manages Zero Touch Provisioning server for automated device provisioning.

### Usage
```bash
python scripts/deploy_ztp.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--config` | PATH | `configs/ztp.yaml` | ZTP configuration file |
| `--fabric` | PATH | `configs/fabric.yaml` | Fabric configuration file |
| `--subnet` | CIDR | Required | Management network subnet |
| `--start-server` | FLAG | False | Start HTTP/TFTP servers |
| `--http-port` | INT | 8080 | HTTP server port |
| `--tftp-port` | INT | 69 | TFTP server port |
| `--generate-only` | FLAG | False | Generate configs without starting server |

### Examples

```bash
# Start ZTP server
python scripts/deploy_ztp.py \
    --subnet 192.168.1.0/24 \
    --start-server

# Generate ZTP configurations only
python scripts/deploy_ztp.py \
    --subnet 192.168.1.0/24 \
    --generate-only

# Custom ports
python scripts/deploy_ztp.py \
    --subnet 192.168.1.0/24 \
    --http-port 8888 \
    --tftp-port 6969 \
    --start-server
```

### DHCP Configuration Generated

```
# ISC DHCP Server configuration
subnet 192.168.1.0 netmask 255.255.255.0 {
    range 192.168.1.100 192.168.1.200;
    option routers 192.168.1.1;
    option tftp-server-name "192.168.1.10";
    option bootfile-name "juniper.conf";
    option vendor-encapsulated-options 01:15:2F:76:61:72:2F:...;
}
```

### Python API

```python
from scripts.deploy_ztp import ZTPServer

# Initialize ZTP server
ztp = ZTPServer(
    subnet='192.168.1.0/24',
    http_port=8080
)

# Generate configurations
ztp.generate_configs()

# Start servers
ztp.start_servers()

# Monitor provisioning
status = ztp.get_provision_status()
```

## manage_rbac.py

### Description
Manages role-based access control for network devices.

### Usage
```bash
python scripts/manage_rbac.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--action` | CHOICE | Required | create\|deploy\|template\|audit |
| `--username` | STRING | - | Username for create action |
| `--role` | CHOICE | - | network_admin\|network_operator\|network_viewer |
| `--devices` | LIST | all | Target devices |
| `--ssh-key` | PATH | - | SSH public key file |
| `--config` | PATH | - | RBAC configuration file |

### Examples

```bash
# Create new user
python scripts/manage_rbac.py \
    --action create \
    --username john.doe \
    --role network_operator \
    --ssh-key ~/.ssh/id_rsa.pub

# Deploy RBAC to all devices
python scripts/manage_rbac.py \
    --action deploy \
    --config configs/rbac.yaml \
    --devices all

# Generate RBAC template
python scripts/manage_rbac.py \
    --action template \
    --output rbac_template.yaml

# Audit user access
python scripts/manage_rbac.py \
    --action audit \
    --devices spine-01,leaf-01
```

### RBAC Configuration Format

```yaml
rbac:
  roles:
    network_admin:
      permissions:
        - "configure"
        - "view"
        - "shell"
      commands:
        - ".*"

    network_operator:
      permissions:
        - "view"
        - "shell"
      commands:
        - "show .*"
        - "clear .*"
        - "ping .*"
        - "traceroute .*"

    network_viewer:
      permissions:
        - "view"
      commands:
        - "show .*"

  users:
    - username: admin
      role: network_admin
      ssh_key: "ssh-rsa AAAAB3..."

    - username: operator
      role: network_operator
      password: "$6$encrypted..."
```

### Python API

```python
from scripts.manage_rbac import RBACManager

# Initialize RBAC manager
rbac = RBACManager()

# Create user
rbac.create_user(
    username='john.doe',
    role='network_operator',
    ssh_key='ssh-rsa AAAAB3...'
)

# Deploy to devices
rbac.deploy(devices=['spine-01', 'leaf-01'])

# Audit access
report = rbac.audit()
```

## validate_fabric.py

### Description
Performs comprehensive validation of the EVPN/VXLAN fabric.

### Usage
```bash
python scripts/validate_fabric.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `-d, --devices` | LIST | Required | Device IPs or hostnames |
| `-u, --username` | STRING | automation | Device username |
| `-p, --password` | STRING | - | Device password |
| `--config` | PATH | - | Fabric configuration file |
| `--report` | CHOICE | text | text\|html\|json |
| `--output` | PATH | - | Report output file |
| `--parallel` | FLAG | False | Validate devices in parallel |
| `--verbose` | FLAG | False | Verbose output |

### Examples

```bash
# Basic validation
python scripts/validate_fabric.py \
    -d 192.168.1.11 \
    -d 192.168.1.21 \
    -u admin

# Full fabric validation with HTML report
python scripts/validate_fabric.py \
    --config configs/fabric.yaml \
    --all-devices \
    --report html \
    --output validation.html

# Parallel validation with JSON output
python scripts/validate_fabric.py \
    -d 192.168.1.11,192.168.1.12,192.168.1.21,192.168.1.22 \
    --parallel \
    --report json \
    --output results.json
```

### Validation Checks

| Check | Description | Criticality |
|-------|-------------|------------|
| `connectivity` | Management connectivity | Critical |
| `bgp_neighbors` | BGP session status | High |
| `evpn_database` | EVPN MAC/IP entries | High |
| `vxlan_vteps` | VTEP discovery | High |
| `vni_mappings` | VNI to VLAN mappings | Medium |
| `interface_status` | Physical interface status | Medium |
| `route_tables` | Routing table entries | Low |
| `config_compliance` | Configuration compliance | Low |

### Python API

```python
from scripts.validate_fabric import FabricValidator

# Initialize validator
validator = FabricValidator(
    devices=['192.168.1.11', '192.168.1.21'],
    username='admin'
)

# Run all validations
results = validator.validate_all()

# Run specific checks
bgp_status = validator.check_bgp()
evpn_status = validator.check_evpn()

# Generate report
validator.generate_report(format='html', output='report.html')
```

## backup_configs.py

### Description
Backs up device configurations with versioning and archival.

### Usage
```bash
python scripts/backup_configs.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--devices` | LIST | all | Devices to backup |
| `--output` | PATH | `backups/` | Backup directory |
| `--format` | CHOICE | text | text\|set\|xml\|json |
| `--compress` | FLAG | False | Compress backup files |
| `--encrypt` | FLAG | False | Encrypt backup files |
| `--retention` | INT | 30 | Retention days |

### Examples

```bash
# Backup all devices
python scripts/backup_configs.py --devices all

# Backup specific devices with compression
python scripts/backup_configs.py \
    --devices spine-01,leaf-01 \
    --compress

# Encrypted backups with retention
python scripts/backup_configs.py \
    --devices all \
    --encrypt \
    --retention 90
```

### Python API

```python
from scripts.backup_configs import ConfigBackup

# Initialize backup manager
backup = ConfigBackup(output_dir='backups/')

# Backup single device
backup.backup_device('192.168.1.11')

# Backup multiple devices
backup.backup_all(compress=True)

# Restore configuration
backup.restore('spine-01', timestamp='20240115_120000')
```

## connect_devices.py

### Description
Simple connectivity testing tool for device reachability.

### Usage
```bash
python scripts/connect_devices.py [OPTIONS]
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--devices` | LIST | Required | Device IPs or hostnames |
| `--username` | STRING | automation | Username |
| `--password` | STRING | - | Password |
| `--timeout` | INT | 30 | Connection timeout |
| `--port` | INT | 22 | SSH port |

### Examples

```bash
# Test single device
python scripts/connect_devices.py --devices 192.168.1.11

# Test multiple devices
python scripts/connect_devices.py \
    --devices 192.168.1.11,192.168.1.21 \
    --username admin \
    --timeout 60
```

### Python API

```python
from scripts.connect_devices import DeviceConnector

# Test connectivity
connector = DeviceConnector()
result = connector.test_device('192.168.1.11')

# Batch testing
results = connector.test_batch(['192.168.1.11', '192.168.1.21'])
```

## Template Functions

### Available Jinja2 Functions

| Function | Description | Example |
|----------|-------------|---------|
| `calculate_ip()` | Calculate IP from base and offset | `{{ calculate_ip('10.0.0.0', 5) }}` |
| `generate_asn()` | Generate ASN from base | `{{ generate_asn(65000, device_id) }}` |
| `vni_to_vlan()` | Convert VNI to VLAN | `{{ vni_to_vlan(10100) }}` |
| `get_peer_ip()` | Get peer IP address | `{{ get_peer_ip(local_ip) }}` |

### Custom Filters

```python
# Custom template filters
@app.template_filter('subnet_host')
def subnet_host(subnet, host_num):
    """Get specific host from subnet"""
    network = ipaddress.ip_network(subnet)
    return str(list(network.hosts())[host_num])

@app.template_filter('increment_asn')
def increment_asn(base_asn, increment):
    """Increment ASN by value"""
    return base_asn + increment
```

## Utility Functions

### Network Utilities

```python
from utils.network import *

# IP address management
next_ip = get_next_ip('10.0.0.0/24')
subnet = calculate_subnet('10.0.0.0/16', 24, 5)

# ASN management
asn = allocate_asn(base=65000, device_type='leaf', device_id=1)

# VXLAN utilities
vni = vlan_to_vni(vlan=100, base=10000)
vtep = get_vtep_ip(loopback_pool='192.168.0.0/24', device_id=1)
```

### Device Utilities

```python
from utils.device import *

# Connection management
device = connect_device('192.168.1.11', username='admin')

# Configuration utilities
config = get_config(device, format='text')
diff = compare_configs(running_config, candidate_config)

# Operational commands
output = run_command(device, 'show bgp summary')
facts = get_device_facts(device)
```

### Validation Utilities

```python
from utils.validation import *

# Input validation
is_valid = validate_ip('192.168.1.1')
is_valid = validate_asn(65000)
is_valid = validate_vni(10100)

# Configuration validation
errors = validate_yaml('configs/fabric.yaml')
is_compliant = check_compliance(device_config, template)
```

---

[Back to Main Documentation](../README.md) | [Architecture Guide](ARCHITECTURE.md) | [Deployment Guide](DEPLOYMENT.md)