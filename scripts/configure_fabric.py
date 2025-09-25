#!/usr/bin/env python3
"""
Configure EVPN/VXLAN fabric with zero trust principles
"""

import yaml
import click
import ipaddress
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table

console = Console()


class FabricBuilder:
    """Build EVPN/VXLAN fabric configurations"""
    
    def __init__(self, config_file):
        self.config = self.load_config(config_file)
        self.env = Environment(loader=FileSystemLoader('../templates'))
        
    def load_config(self, config_file):
        """Load fabric configuration from YAML"""
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def generate_underlay_ips(self):
        """Generate IP addresses for underlay network"""
        network = ipaddress.IPv4Network(self.config['fabric']['underlay']['ipv4_pool'])
        hosts = list(network.hosts())
        
        assignments = {
            'spines': [],
            'leafs': [],
            'p2p_links': []
        }
        
        # Assign loopbacks
        loopback_net = ipaddress.IPv4Network(self.config['fabric']['underlay']['loopback_pool'])
        loopback_hosts = list(loopback_net.hosts())
        
        # Spine loopbacks
        for i in range(self.config['spines']['count']):
            assignments['spines'].append({
                'name': f"spine{i+1}",
                'loopback': str(loopback_hosts[i]),
                'asn': self.config['fabric']['asn'] + i
            })
        
        # Leaf loopbacks
        for i in range(self.config['leafs']['count']):
            idx = self.config['spines']['count'] + i
            assignments['leafs'].append({
                'name': f"leaf{i+1}",
                'loopback': str(loopback_hosts[idx]),
                'asn': self.config['fabric']['asn'] + 100 + i
            })
        
        # Generate P2P links
        link_idx = 0
        for spine in assignments['spines']:
            for leaf in assignments['leafs']:
                subnet = ipaddress.IPv4Network(f"10.{link_idx}.{link_idx}.0/31")
                assignments['p2p_links'].append({
                    'spine': spine['name'],
                    'leaf': leaf['name'],
                    'spine_ip': str(list(subnet.hosts())[0]),
                    'leaf_ip': str(list(subnet.hosts())[1])
                })
                link_idx += 1
        
        return assignments
    
    def generate_vxlan_config(self, zone):
        """Generate VXLAN configuration for a zone"""
        vni_base = zone['vni_base']
        configs = []
        
        for idx, subnet in enumerate(zone['subnets']):
            vlan_id = 100 + idx
            vni = vni_base + idx
            
            configs.append({
                'zone': zone['name'],
                'vlan_id': vlan_id,
                'vni': vni,
                'subnet': subnet,
                'gateway': str(list(ipaddress.IPv4Network(subnet).hosts())[0])
            })
        
        return configs
    
    def render_spine_config(self, spine_data):
        """Render spine switch configuration"""
        template = self.env.get_template('spine.j2')
        return template.render(spine=spine_data, config=self.config)
    
    def render_leaf_config(self, leaf_data):
        """Render leaf switch configuration"""
        template = self.env.get_template('leaf.j2')
        return template.render(leaf=leaf_data, config=self.config)
    
    def display_summary(self, assignments):
        """Display configuration summary"""
        # Spine table
        spine_table = Table(title="Spine Switches")
        spine_table.add_column("Name", style="cyan")
        spine_table.add_column("Loopback", style="green")
        spine_table.add_column("ASN", style="yellow")
        
        for spine in assignments['spines']:
            spine_table.add_row(spine['name'], spine['loopback'], str(spine['asn']))
        
        console.print(spine_table)
        
        # Leaf table
        leaf_table = Table(title="Leaf Switches")
        leaf_table.add_column("Name", style="cyan")
        leaf_table.add_column("Loopback", style="green")
        leaf_table.add_column("ASN", style="yellow")
        
        for leaf in assignments['leafs']:
            leaf_table.add_row(leaf['name'], leaf['loopback'], str(leaf['asn']))
        
        console.print(leaf_table)
    
    def save_configs(self, assignments):
        """Save generated configurations to files"""
        output_dir = Path('../configs/generated')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save spine configs
        for spine in assignments['spines']:
            config = self.render_spine_config(spine)
            with open(output_dir / f"{spine['name']}.conf", 'w') as f:
                f.write(config)
            console.print(f"[green]✓[/green] Generated config for {spine['name']}")
        
        # Save leaf configs
        for leaf in assignments['leafs']:
            config = self.render_leaf_config(leaf)
            with open(output_dir / f"{leaf['name']}.conf", 'w') as f:
                f.write(config)
            console.print(f"[green]✓[/green] Generated config for {leaf['name']}")


@click.command()
@click.option('--config', default='../configs/fabric.yaml', help='Fabric configuration file')
@click.option('--output', default='../configs/generated', help='Output directory for configs')
@click.option('--dry-run', is_flag=True, help='Display config without saving')
def main(config, output, dry_run):
    """Generate EVPN/VXLAN fabric configuration"""
    console.print("[bold blue]EVPN/VXLAN Fabric Builder[/bold blue]")
    
    builder = FabricBuilder(config)
    assignments = builder.generate_underlay_ips()
    
    builder.display_summary(assignments)
    
    if not dry_run:
        builder.save_configs(assignments)
        console.print("\n[bold green]Configuration files generated successfully![/bold green]")
    else:
        console.print("\n[yellow]Dry run mode - no files saved[/yellow]")


if __name__ == '__main__':
    main()
