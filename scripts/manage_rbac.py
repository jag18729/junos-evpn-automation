#!/usr/bin/env python3
"""
Configure Role-Based Access Control for Junos devices
"""

import yaml
import click
import hashlib
from pathlib import Path
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from rich.console import Console

console = Console()


class RBACManager:
    """Manage RBAC policies for Junos devices"""
    
    def __init__(self):
        self.roles = {
            'network_admin': {
                'class': 'super-user',
                'permissions': 'all'
            },
            'network_operator': {
                'class': 'operator',
                'permissions': [
                    'clear',
                    'network',
                    'reset',
                    'trace',
                    'view'
                ]
            },
            'network_viewer': {
                'class': 'read-only',
                'permissions': [
                    'view'
                ]
            },
            'security_admin': {
                'class': 'security-admin',
                'permissions': [
                    'security',
                    'firewall',
                    'flow',
                    'vpn'
                ]
            }
        }
        
    def create_user(self, username, password, role):
        """Generate user configuration"""
        # Hash password (simplified - use proper hashing in production)
        hashed = hashlib.sha256(password.encode()).hexdigest()
        
        config = f"""
        system {{
            login {{
                user {username} {{
                    uid 2000;
                    class {self.roles[role]['class']};
                    authentication {{
                        encrypted-password "{hashed}";
                    }}
                }}
            }}
        }}
        """
        return config
    
    def create_custom_class(self, class_name, permissions):
        """Create custom login class"""
        perm_string = ' '.join(permissions)
        
        config = f"""
        system {{
            login {{
                class {class_name} {{
                    permissions [ {perm_string} ];
                }}
            }}
        }}
        """
        return config
    
    def apply_zero_trust_policies(self):
        """Generate zero trust access policies"""
        policies = """
        system {
            services {
                ssh {
                    root-login deny;
                    protocol-version v2;
                    connection-limit 10;
                    rate-limit 5;
                }
                netconf {
                    ssh {
                        connection-limit 10;
                    }
                }
            }
            login {
                retry-options {
                    tries-before-disconnect 3;
                    backoff-threshold 3;
                    backoff-factor 5;
                    minimum-time 30;
                }
                message "Authorized access only. All activities are logged.";
            }
        }
        
        firewall {
            family inet {
                filter PROTECT_RE {
                    term SSH_LIMIT {
                        from {
                            source-prefix-list {
                                MANAGEMENT_NETWORKS;
                            }
                            protocol tcp;
                            destination-port ssh;
                        }
                        then {
                            policer SSH_POLICER;
                            accept;
                        }
                    }
                    term SSH_DENY {
                        from {
                            protocol tcp;
                            destination-port ssh;
                        }
                        then {
                            log;
                            reject;
                        }
                    }
                }
            }
            policer SSH_POLICER {
                if-exceeding {
                    bandwidth-limit 1m;
                    burst-size-limit 100k;
                }
                then discard;
            }
        }
        
        policy-options {
            prefix-list MANAGEMENT_NETWORKS {
                10.0.0.0/8;
                192.168.0.0/16;
            }
        }
        """
        return policies
    
    def generate_audit_config(self):
        """Generate audit logging configuration"""
        config = """
        system {
            syslog {
                user * {
                    any emergency;
                }
                host 192.168.1.100 {
                    any notice;
                    authorization info;
                    facility-override local7;
                    log-prefix AUDIT;
                }
                file interactive-commands {
                    interactive-commands any;
                    archive size 10m files 10;
                }
                file security {
                    authorization info;
                    archive size 10m files 10;
                }
            }
            accounting {
                events [ login change-log interactive-commands ];
                destination {
                    radius {
                        server {
                            192.168.1.101 {
                                secret "$9$encrypted$secret";
                                timeout 5;
                                retry 3;
                            }
                        }
                    }
                }
            }
        }
        """
        return config
    
    def deploy_to_device(self, host, username, password, config):
        """Deploy RBAC configuration to device"""
        try:
            device = Device(host=host, user=username, password=password)
            device.open()
            
            with Config(device) as cu:
                cu.load(config, format='text')
                cu.commit(comment='RBAC configuration applied')
            
            device.close()
            return True
        except Exception as e:
            console.print(f"[red]Error deploying to {host}: {e}[/red]")
            return False
    
    def save_rbac_template(self, output_dir):
        """Save RBAC template configuration"""
        template = {
            'roles': self.roles,
            'users': [
                {'name': 'admin', 'role': 'network_admin'},
                {'name': 'operator', 'role': 'network_operator'},
                {'name': 'viewer', 'role': 'network_viewer'}
            ],
            'zero_trust': {
                'enabled': True,
                'management_networks': ['10.0.0.0/8', '192.168.0.0/16'],
                'max_sessions': 10,
                'session_timeout': 900
            }
        }
        
        output_path = Path(output_dir) / 'rbac_template.yaml'
        with open(output_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
        
        console.print(f"[green]✓[/green] RBAC template saved to {output_path}")


@click.command()
@click.option('--action', type=click.Choice(['create', 'deploy', 'template']), required=True)
@click.option('--username', help='Username to create')
@click.option('--role', type=click.Choice(['network_admin', 'network_operator', 'network_viewer']))
@click.option('--device', help='Device IP address')
@click.option('--output', default='../rbac', help='Output directory')
def main(action, username, role, device, output):
    """Manage RBAC configurations"""
    console.print("[bold blue]RBAC Configuration Manager[/bold blue]")
    
    rbac = RBACManager()
    
    if action == 'create':
        if not username or not role:
            console.print("[red]Username and role required for create action[/red]")
            return
        
        password = click.prompt('Password', hide_input=True)
        config = rbac.create_user(username, password, role)
        
        # Save configuration
        output_path = Path(output) / f"{username}_rbac.conf"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(config)
        
        console.print(f"[green]✓[/green] RBAC configuration created for {username}")
    
    elif action == 'deploy':
        if not device:
            console.print("[red]Device IP required for deploy action[/red]")
            return
        
        # Generate full RBAC config
        config = rbac.apply_zero_trust_policies()
        config += rbac.generate_audit_config()
        
        admin_user = click.prompt('Admin username')
        admin_pass = click.prompt('Admin password', hide_input=True)
        
        if rbac.deploy_to_device(device, admin_user, admin_pass, config):
            console.print(f"[green]✓[/green] RBAC deployed to {device}")
    
    elif action == 'template':
        rbac.save_rbac_template(output)
        
        # Also save zero trust policies
        zt_config = rbac.apply_zero_trust_policies()
        zt_path = Path(output) / 'zero_trust.conf'
        with open(zt_path, 'w') as f:
            f.write(zt_config)
        console.print(f"[green]✓[/green] Zero trust policies saved to {zt_path}")
        
        # Save audit config
        audit_config = rbac.generate_audit_config()
        audit_path = Path(output) / 'audit.conf'
        with open(audit_path, 'w') as f:
            f.write(audit_config)
        console.print(f"[green]✓[/green] Audit configuration saved to {audit_path}")


if __name__ == '__main__':
    main()
