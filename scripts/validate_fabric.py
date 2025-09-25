#!/usr/bin/env python3
"""
Validate EVPN/VXLAN fabric deployment
"""

import click
import time
from concurrent.futures import ThreadPoolExecutor
from jnpr.junos import Device
from jnpr.junos.op.routes import RouteTable
from rich.console import Console
from rich.table import Table
from rich.progress import track

console = Console()


class FabricValidator:
    """Validate EVPN/VXLAN fabric health"""
    
    def __init__(self, devices):
        self.devices = devices
        self.results = {}
        
    def connect_device(self, host, username, password):
        """Connect to Junos device"""
        try:
            device = Device(host=host, user=username, password=password)
            device.open()
            return device
        except Exception as e:
            console.print(f"[red]Failed to connect to {host}: {e}[/red]")
            return None
    
    def check_bgp_neighbors(self, device):
        """Check BGP neighbor status"""
        result = device.rpc.get_bgp_summary_information()
        neighbors = []
        
        for peer in result.findall('.//bgp-peer'):
            peer_addr = peer.find('peer-address').text
            peer_state = peer.find('peer-state').text
            neighbors.append({
                'address': peer_addr,
                'state': peer_state,
                'status': 'UP' if peer_state == 'Established' else 'DOWN'
            })
        
        return neighbors
    
    def check_evpn_database(self, device):
        """Check EVPN database entries"""
        result = device.rpc.get_evpn_database_information()
        entries = []
        
        for instance in result.findall('.//evpn-database-instance'):
            name = instance.find('evpn-database-instance-name').text
            mac_count = len(instance.findall('.//mac-entry'))
            entries.append({
                'instance': name,
                'mac_count': mac_count
            })
        
        return entries
    
    def check_vxlan_vteps(self, device):
        """Check VXLAN VTEP status"""
        result = device.rpc.get_ethernet_switching_vxlan_tunnel_end_point_remote()
        vteps = []
        
        for vtep in result.findall('.//vxlan-tunnel-end-point'):
            remote_ip = vtep.find('remote-vtep-address').text
            vni = vtep.find('vxlan-tunnel-end-point-vni').text
            vteps.append({
                'remote_ip': remote_ip,
                'vni': vni,
                'status': 'Active'
            })
        
        return vteps
    
    def check_interface_status(self, device):
        """Check interface status"""
        result = device.rpc.get_interface_information(terse=True)
        interfaces = []
        
        for intf in result.findall('.//physical-interface'):
            name = intf.find('name').text
            admin = intf.find('admin-status').text
            oper = intf.find('oper-status').text
            
            if name.startswith(('et-', 'xe-', 'ge-')):
                interfaces.append({
                    'name': name,
                    'admin': admin,
                    'oper': oper,
                    'status': 'UP' if oper == 'up' else 'DOWN'
                })
        
        return interfaces
    
    def ping_test(self, device, target):
        """Perform ping test"""
        try:
            result = device.rpc.ping(host=target, count='5')
            packet_loss = result.find('.//packet-loss').text
            return {
                'target': target,
                'loss': packet_loss,
                'status': 'OK' if packet_loss == '0' else 'FAIL'
            }
        except:
            return {
                'target': target,
                'loss': '100',
                'status': 'FAIL'
            }
    
    def validate_device(self, host, username, password):
        """Run all validation checks on a device"""
        device = self.connect_device(host, username, password)
        if not device:
            return None
        
        results = {
            'host': host,
            'bgp': self.check_bgp_neighbors(device),
            'evpn': self.check_evpn_database(device),
            'vxlan': self.check_vxlan_vteps(device),
            'interfaces': self.check_interface_status(device)
        }
        
        device.close()
        return results
    
    def run_validation(self, username, password):
        """Run validation on all devices"""
        console.print("[yellow]Starting fabric validation...[/yellow]")
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for device in self.devices:
                future = executor.submit(
                    self.validate_device,
                    device,
                    username,
                    password
                )
                futures.append((device, future))
            
            for device, future in track(futures, description="Validating devices..."):
                result = future.result()
                if result:
                    self.results[device] = result
    
    def display_results(self):
        """Display validation results"""
        # BGP Summary
        bgp_table = Table(title="BGP Neighbor Status")
        bgp_table.add_column("Device", style="cyan")
        bgp_table.add_column("Neighbor", style="white")
        bgp_table.add_column("State", style="white")
        bgp_table.add_column("Status", style="white")
        
        for device, data in self.results.items():
            for neighbor in data.get('bgp', []):
                status_color = "green" if neighbor['status'] == 'UP' else "red"
                bgp_table.add_row(
                    device,
                    neighbor['address'],
                    neighbor['state'],
                    f"[{status_color}]{neighbor['status']}[/{status_color}]"
                )
        
        console.print(bgp_table)
        
        # EVPN Summary
        evpn_table = Table(title="EVPN Database")
        evpn_table.add_column("Device", style="cyan")
        evpn_table.add_column("Instance", style="white")
        evpn_table.add_column("MAC Count", style="yellow")
        
        for device, data in self.results.items():
            for entry in data.get('evpn', []):
                evpn_table.add_row(
                    device,
                    entry['instance'],
                    str(entry['mac_count'])
                )
        
        console.print(evpn_table)
        
        # VXLAN VTEP Summary
        vtep_table = Table(title="VXLAN VTEPs")
        vtep_table.add_column("Device", style="cyan")
        vtep_table.add_column("Remote VTEP", style="white")
        vtep_table.add_column("VNI", style="yellow")
        
        for device, data in self.results.items():
            for vtep in data.get('vxlan', []):
                vtep_table.add_row(
                    device,
                    vtep['remote_ip'],
                    vtep['vni']
                )
        
        console.print(vtep_table)
    
    def generate_report(self, output_file):
        """Generate validation report"""
        report = []
        report.append("EVPN/VXLAN Fabric Validation Report")
        report.append("=" * 50)
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        for device, data in self.results.items():
            report.append(f"\nDevice: {device}")
            report.append("-" * 30)
            
            # BGP Status
            bgp_up = sum(1 for n in data.get('bgp', []) if n['status'] == 'UP')
            bgp_total = len(data.get('bgp', []))
            report.append(f"BGP Neighbors: {bgp_up}/{bgp_total} UP")
            
            # EVPN Status
            evpn_instances = len(data.get('evpn', []))
            total_macs = sum(e['mac_count'] for e in data.get('evpn', []))
            report.append(f"EVPN Instances: {evpn_instances}, Total MACs: {total_macs}")
            
            # VXLAN Status
            vtep_count = len(data.get('vxlan', []))
            report.append(f"VXLAN VTEPs: {vtep_count}")
            
            # Interface Status
            intf_up = sum(1 for i in data.get('interfaces', []) if i['status'] == 'UP')
            intf_total = len(data.get('interfaces', []))
            report.append(f"Interfaces: {intf_up}/{intf_total} UP")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(report))
        
        console.print(f"[green]✓[/green] Report saved to {output_file}")


@click.command()
@click.option('--devices', '-d', multiple=True, required=True, help='Device IPs to validate')
@click.option('--username', '-u', prompt=True, help='Device username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Device password')
@click.option('--report', default='validation_report.txt', help='Output report file')
def main(devices, username, password, report):
    """Validate EVPN/VXLAN fabric deployment"""
    console.print("[bold blue]Fabric Validation Tool[/bold blue]")
    
    validator = FabricValidator(devices)
    validator.run_validation(username, password)
    
    if validator.results:
        validator.display_results()
        validator.generate_report(report)
        
        # Overall health check
        total_devices = len(validator.results)
        console.print(f"\n[bold]Validation Summary:[/bold]")
        console.print(f"Devices validated: {total_devices}")
        
        all_bgp_up = all(
            all(n['status'] == 'UP' for n in data.get('bgp', []))
            for data in validator.results.values()
        )
        
        if all_bgp_up:
            console.print("[bold green]✓ Fabric health: GOOD[/bold green]")
        else:
            console.print("[bold red]⚠ Fabric health: ISSUES DETECTED[/bold red]")
    else:
        console.print("[red]No validation results collected[/red]")


if __name__ == '__main__':
    main()
