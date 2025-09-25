#!/usr/bin/env python3
"""
Quick example: Configure VXLAN on a single device
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config


def quick_vxlan_setup(host, username, password):
    """Quick VXLAN configuration example"""
    
    # Connect to device
    device = Device(host=host, user=username, password=password)
    device.open()
    
    # VXLAN configuration
    vxlan_config = """
    vlans {
        VLAN100 {
            vlan-id 100;
            vxlan {
                vni 10100;
            }
        }
    }
    
    protocols {
        evpn {
            encapsulation vxlan;
            extended-vni-list all;
        }
    }
    
    switch-options {
        vtep-source-interface lo0.0;
        route-distinguisher 1.1.1.1:1;
        vrf-target target:65000:1;
    }
    """
    
    # Load and commit configuration
    with Config(device) as cu:
        cu.load(vxlan_config, format='text')
        cu.commit(comment='Quick VXLAN setup')
    
    device.close()
    print(f"VXLAN configured on {host}")


if __name__ == '__main__':
    # Example usage
    host = input("Device IP: ")
    username = input("Username: ")
    password = input("Password: ")
    
    quick_vxlan_setup(host, username, password)
