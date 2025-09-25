#!/usr/bin/env python3
"""
Deploy Zero Touch Provisioning for Junos devices
"""

import os
import yaml
import click
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console

console = Console()


class ZTPServer:
    """Manage ZTP server for Junos devices"""
    
    def __init__(self):
        self.ztp_dir = Path('../ztp')
        self.dhcp_config = []
        self.http_root = '/var/www/html/ztp'
        
    def generate_dhcp_config(self, subnet, devices):
        """Generate ISC DHCP configuration"""
        dhcp_template = """
        # ZTP DHCP Configuration
        subnet {subnet} netmask {netmask} {{
            range {range_start} {range_end};
            option routers {gateway};
            option domain-name-servers 8.8.8.8, 8.8.4.4;
            
            # Juniper ZTP options
            option option-150 code 150 = ip-address;
            option option-150 {ztp_server};
            option vendor-encapsulated-options 00:00:00:09:0c:74:65:73:74:2d:63:6f:6e:66:69:67;
            
            # Device specific configurations
            {device_configs}
        }}
        """
        
        device_entries = []
        for device in devices:
            entry = f"""
            host {device['hostname']} {{
                hardware ethernet {device['mac']};
                fixed-address {device['ip']};
                option host-name "{device['hostname']}";
                filename "{device['config_file']}";
            }}
            """
            device_entries.append(entry)
        
        return dhcp_template.format(
            subnet=subnet.split('/')[0],
            netmask='255.255.255.0',
            range_start=subnet.replace('.0/24', '.100'),
            range_end=subnet.replace('.0/24', '.200'),
            gateway=subnet.replace('.0/24', '.1'),
            ztp_server=subnet.replace('.0/24', '.10'),
            device_configs=''.join(device_entries)
        )
    
    def create_ztp_script(self, device_name, config_url):
        """Create ZTP script for device"""
        script = f"""#!/bin/sh
        # ZTP Script for {device_name}
        
        echo "Starting ZTP for {device_name}"
        
        # Download configuration
        curl -o /var/tmp/ztp.conf {config_url}/{device_name}.conf
        
        # Apply configuration
        cli <<EOF
        configure
        load override /var/tmp/ztp.conf
        commit and-quit
        EOF
        
        # Set secure root password
        cli <<EOF
        configure
        set system root-authentication encrypted-password "$6$encrypted$password"
        commit and-quit
        EOF
        
        echo "ZTP completed for {device_name}"
        """
        return script
    
    def setup_file_server(self):
        """Setup HTTP server for ZTP files"""
        console.print("[yellow]Setting up ZTP file server...[/yellow]")
        
        # Create directories
        self.ztp_dir.mkdir(parents=True, exist_ok=True)
        (self.ztp_dir / 'configs').mkdir(exist_ok=True)
        (self.ztp_dir / 'scripts').mkdir(exist_ok=True)
        (self.ztp_dir / 'images').mkdir(exist_ok=True)
        
        # Create simple HTTP server script
        server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8080
DIRECTORY = "."

class ZTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

os.chdir('/home/claude/junos-evpn-automation/ztp')
with socketserver.TCPServer(("", PORT), ZTPHandler) as httpd:
    print(f"ZTP server running on port {PORT}")
    httpd.serve_forever()
        """
        
        with open(self.ztp_dir / 'server.py', 'w') as f:
            f.write(server_script)
        
        os.chmod(self.ztp_dir / 'server.py', 0o755)
        console.print("[green]✓[/green] ZTP file server script created")
    
    def generate_device_list(self, fabric_config):
        """Generate device list from fabric configuration"""
        devices = []
        
        # Add spines
        for i in range(fabric_config['spines']['count']):
            devices.append({
                'hostname': f"spine{i+1}",
                'mac': f"00:00:00:00:01:{i+1:02x}",  # Placeholder MAC
                'ip': f"192.168.1.{10+i}",
                'config_file': f"spine{i+1}.conf"
            })
        
        # Add leafs
        for i in range(fabric_config['leafs']['count']):
            devices.append({
                'hostname': f"leaf{i+1}",
                'mac': f"00:00:00:00:02:{i+1:02x}",  # Placeholder MAC
                'ip': f"192.168.1.{20+i}",
                'config_file': f"leaf{i+1}.conf"
            })
        
        return devices
    
    def create_phone_home_script(self):
        """Create phone-home script for devices"""
        script = """#!/bin/sh
        # Phone home script for Junos devices
        
        MGMT_IP=$(ifconfig vme0 | grep "inet " | awk '{print $2}')
        HOSTNAME=$(hostname)
        
        # Register with management server
        curl -X POST http://192.168.1.10:8081/register \
             -H "Content-Type: application/json" \
             -d '{
                "hostname": "'$HOSTNAME'",
                "ip": "'$MGMT_IP'",
                "status": "provisioned"
             }'
        
        # Start NETCONF
        cli <<EOF
        configure
        set system services netconf ssh
        commit
        EOF
        """
        
        with open(self.ztp_dir / 'scripts' / 'phone_home.sh', 'w') as f:
            f.write(script)
        
        console.print("[green]✓[/green] Phone-home script created")


@click.command()
@click.option('--subnet', default='192.168.1.0/24', help='Management subnet for ZTP')
@click.option('--config', default='../configs/fabric.yaml', help='Fabric configuration file')
@click.option('--start-server', is_flag=True, help='Start ZTP HTTP server')
def main(subnet, config, start_server):
    """Deploy Zero Touch Provisioning server"""
    console.print("[bold blue]ZTP Deployment Tool[/bold blue]")
    
    # Load fabric config
    with open(config, 'r') as f:
        fabric_config = yaml.safe_load(f)
    
    ztp = ZTPServer()
    
    # Setup file server
    ztp.setup_file_server()
    
    # Generate device list
    devices = ztp.generate_device_list(fabric_config)
    
    # Generate DHCP config
    dhcp_config = ztp.generate_dhcp_config(subnet, devices)
    with open(ztp.ztp_dir / 'dhcpd.conf', 'w') as f:
        f.write(dhcp_config)
    console.print("[green]✓[/green] DHCP configuration generated")
    
    # Create ZTP scripts for each device
    for device in devices:
        script = ztp.create_ztp_script(
            device['hostname'],
            f"http://{subnet.replace('.0/24', '.10')}:8080/configs"
        )
        script_path = ztp.ztp_dir / 'scripts' / f"{device['hostname']}_ztp.sh"
        with open(script_path, 'w') as f:
            f.write(script)
        os.chmod(script_path, 0o755)
    
    console.print(f"[green]✓[/green] Created ZTP scripts for {len(devices)} devices")
    
    # Create phone-home script
    ztp.create_phone_home_script()
    
    # Copy configs to ZTP directory
    src_configs = Path('../configs/generated')
    dst_configs = ztp.ztp_dir / 'configs'
    if src_configs.exists():
        shutil.copytree(src_configs, dst_configs, dirs_exist_ok=True)
        console.print("[green]✓[/green] Device configs copied to ZTP directory")
    
    if start_server:
        console.print("\n[yellow]Starting ZTP HTTP server on port 8080...[/yellow]")
        os.system(f"cd {ztp.ztp_dir} && python3 server.py")


if __name__ == '__main__':
    main()
