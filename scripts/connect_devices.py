#!/usr/bin/env python3
"""
Simple script to connect and get facts from Junos devices
"""

import click
from jnpr.junos import Device
from rich.console import Console
from rich.table import Table

console = Console()


def get_device_facts(host, username, password):
    """Get basic facts from a Junos device"""
    try:
        device = Device(host=host, user=username, password=password)
        device.open()
        
        facts = device.facts
        device.close()
        
        return {
            'hostname': facts.get('hostname', 'Unknown'),
            'model': facts.get('model', 'Unknown'),
            'version': facts.get('version', 'Unknown'),
            'serial': facts.get('serialnumber', 'Unknown'),
            'uptime': facts.get('RE0', {}).get('up_time', 'Unknown'),
            'status': 'Connected'
        }
    except Exception as e:
        return {
            'hostname': host,
            'status': f'Failed: {str(e)}'
        }


@click.command()
@click.option('--host', '-h', multiple=True, required=True, help='Device IP addresses')
@click.option('--username', '-u', prompt=True, help='Username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
def main(host, username, password):
    """Connect to Junos devices and get facts"""
    console.print("[bold blue]Junos Device Connection Tool[/bold blue]\n")
    
    # Create results table
    table = Table(title="Device Facts")
    table.add_column("Host", style="cyan")
    table.add_column("Hostname", style="green")
    table.add_column("Model", style="yellow")
    table.add_column("Version", style="magenta")
    table.add_column("Serial", style="white")
    table.add_column("Status", style="white")
    
    for device_host in host:
        console.print(f"Connecting to {device_host}...")
        facts = get_device_facts(device_host, username, password)
        
        if facts.get('status') == 'Connected':
            table.add_row(
                device_host,
                facts.get('hostname', 'N/A'),
                facts.get('model', 'N/A'),
                facts.get('version', 'N/A'),
                facts.get('serial', 'N/A'),
                "[green]Connected[/green]"
            )
        else:
            table.add_row(
                device_host,
                'N/A',
                'N/A',
                'N/A',
                'N/A',
                f"[red]{facts.get('status', 'Failed')}[/red]"
            )
    
    console.print(table)


if __name__ == '__main__':
    main()
