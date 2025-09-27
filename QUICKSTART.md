# 🚀 Quick Start Guide - Junos EVPN/VXLAN Automation

## 5-Minute Setup

### Step 1: Install & Setup
```bash
# Clone and enter directory
git clone https://github.com/jag18729/junos-evpn-automation.git
cd junos-evpn-automation

# Run automated setup
./setup.sh

# Activate environment
source venv/bin/activate
```

### Step 2: Configure Devices
Edit `configs/fabric.yaml`:
```yaml
devices:
  - hostname: spine1.example.com
    username: admin
    password: Admin123!
    role: spine
  - hostname: leaf1.example.com
    username: admin
    password: Admin123!
    role: leaf
```

### Step 3: Deploy
```bash
# Connect and configure all devices
python scripts/configure_fabric.py

# Validate the deployment
python scripts/validate_fabric.py
```

## ✅ That's It!

Your EVPN/VXLAN fabric is now configured and running.

## Next Steps

### Enable ZTP (Optional)
```bash
python scripts/deploy_ztp.py
```

### Setup RBAC
```bash
python scripts/manage_rbac.py --role admin --user john
```

### Create Backup
```bash
python scripts/backup_configs.py
```

## Common Commands

| Task | Command |
|------|---------|
| Check fabric status | `python scripts/validate_fabric.py` |
| Add new VXLAN | `python examples/quick_vxlan.py --vni 10001` |
| Backup configs | `python scripts/backup_configs.py` |
| View device info | `python scripts/connect_devices.py --show` |

## Troubleshooting

### Can't connect to devices?
```bash
# Test connectivity
ping spine1.example.com

# Verify SSH access
ssh admin@spine1.example.com
```

### Configuration failed?
```bash
# Check logs
tail -f logs/fabric_config.log

# Validate YAML syntax
python -m yaml configs/fabric.yaml
```

### Need help?
- Read [Full Documentation](DOCUMENTATION.md)
- Check [Architecture Guide](docs/ARCHITECTURE.md)
- Review [Deployment Guide](docs/DEPLOYMENT.md)

## Example Configurations

### Small Lab (2+4)
```bash
cp examples/small_fabric.yaml configs/fabric.yaml
python scripts/configure_fabric.py
```

### Quick VXLAN Test
```python
from examples.quick_vxlan import quick_deploy
quick_deploy(vni=5000, vlan=100, name="Test-Tenant")
```

## Tips

1. **Always validate** before and after changes
2. **Backup regularly** using the backup script
3. **Use ZTP** for new device deployments
4. **Enable RBAC** before production use
5. **Monitor logs** in the logs/ directory