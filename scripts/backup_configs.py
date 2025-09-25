#!/usr/bin/env python3
"""
Backup configurations from Junos devices
"""

import click
import os
from datetime import datetime
from pathlib import Path
from jnpr.junos import Device
from rich.console import Console

console = Console()


def backup_device_config(host, username, password, backup_dir):
    """Backup configuration from a single device"""
    try:
        device = Device(host=host, user=username, password=password)
        device.open()
        
        # Get configuration
        config = device.rpc.get_config(options={'format': 'text'})
        config_text = config.text
        
        # Get device hostname
        hostname = device.facts.get('hostname', host)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{hostname}_{timestamp}.conf"
        filepath = backup_dir / filename
        
        # Save configuration
        with open(filepath, 'w') as f:
            f.write(config_text)
        
        device.close()
        
        return {
            'status': 'success',
            'hostname': hostname,
            'file': str(filepath)
        }
        
    except Exception as e:
        return {
            'status': 'failed',
            'hostname': host,
            'error': str(e)
        }


@click.command()
@click.option('--host', '-h', multiple=True, required=True, help='Device IP addresses')
@click.option('--username', '-u', prompt=True, help='Username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
@click.option('--backup-dir', default='backups', help='Backup directory')
def main(host, username, password, backup_dir):
    """Backup Junos device configurations"""
    console.print("[bold blue]Configuration Backup Tool[/bold blue]\n")
    
    # Create backup directory
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Backup each device
    for device_host in host:
        console.print(f"Backing up {device_host}...")
        result = backup_device_config(device_host, username, password, backup_path)
        
        if result['status'] == 'success':
            console.print(f"[green]✓[/green] {result['hostname']} backed up to {result['file']}")
        else:
            console.print(f"[red]✗[/red] {result['hostname']}: {result['error']}")
    
    console.print(f"\n[bold]Backups saved to: {backup_path}[/bold]")


if __name__ == '__main__':
    main()
