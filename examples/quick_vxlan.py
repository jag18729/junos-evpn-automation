#!/usr/bin/env python3
"""
Quick example: Configure VXLAN on a single device
"""

from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import ConnectError, ConfigLoadError, CommitError, RpcError


def quick_vxlan_setup(host, username, password):
    """Quick VXLAN configuration example"""
    
    # Basic input validation
    if not host or not username or not password:
        print("Error: host, username, and password are required.")
        return

    device = Device(host=host, user=username, password=password)
    try:
        device.open()
    except ConnectError as exc:
        print(f"Connection failed to {host}: {exc}")
        return
    except Exception as exc:
        print(f"Unexpected error opening connection to {host}: {exc}")
        return
    
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
    try:
        with Config(device) as cu:
            try:
                cu.load(vxlan_config, format='text')
            except ConfigLoadError as exc:
                print(f"Failed to load configuration on {host}: {exc}")
                return
            except RpcError as exc:
                print(f"RPC error during load on {host}: {exc}")
                return

            try:
                cu.commit(comment='Quick VXLAN setup')
            except CommitError as exc:
                print(f"Commit failed on {host}: {exc}")
                return
            except RpcError as exc:
                print(f"RPC error during commit on {host}: {exc}")
                return
    finally:
        try:
            if device and device.connected:
                device.close()
        except Exception as exc:
            print(f"Warning: failed to close connection to {host}: {exc}")

    print(f"VXLAN configured on {host}")


if __name__ == '__main__':
    # Example usage
    try:
        host = input("Device IP: ")
        username = input("Username: ")
        password = input("Password: ")
        quick_vxlan_setup(host, username, password)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
