#!/usr/bin/env python

import sys
import argparse
import os
from pathlib import PosixPath
import shlex
import subprocess

RANCHER_VERSION = os.environ.get('RANCHER_VERSION', 'v2.2.5')

def get_args():
    parser = argparse.ArgumentParser(
		prog=os.path.basename(sys.argv[0]),
		description='Bootstrap rancher nodes')
    
    parser.add_argument('-u', '--user', action='store', required=True, help='SSH user')
    parser.add_argument('-p', '--port', action='store', type=int, default=22, help='SSH port')
    parser.add_argument('-k', '--key', action='store', type=PosixPath, required=True, help='Path to the ssh key')
    parser.add_argument('-m', '--manager', action='store', help='url for manager api')
    parser.add_argument('-n', '--node', action='append',  help='Hosts to provision', dest='nodes', default=[])
    parser.add_argument('-t', '--rancher-token', action='store', help='Rancher registration token')
    parser.add_argument('--etcd', action='store_true', help='Register as an ectd node')
    parser.add_argument('--controlplane', action='store_true', help='Register as a controlplane node')
    parser.add_argument('--worker', action='store_true', help='Register as a worker node')
    return parser.parse_args()

args = get_args()

def get_docker_cmd(name='node', manager=None, token=None, rancher_agent_ver=RANCHER_VERSION,
                public_ip=None, private_ip=None, etcd=False, controlplane=False, 
                worker=False, container_name='rancher-manager', sudo=True, restart='unless-stopped'):
    sudo = 'sudo' if sudo else ''
    restart = f'--restart={restart}' if restart is not None else ''
    public_ip = f'--address {public_ip}' if public_ip is not None else ''
    private_ip = f'--internal-address {private_ip}' if private_ip is not None else ''
    etcd = '--etcd' if etcd else ''
    controlplane = '--controlplane' if controlplane else ''
    worker = '--worker' if worker else ''
    cmd = f'{sudo} docker run -d --privileged {restart} ' + \
            '--net=host -v="/etc/kubernetes:/etc/kubernetes" ' + \
           f'-v="/var/run:/var/run" rancher/rancher-agent:{rancher_agent_ver} ' + \
           f'--server {manager} ' + \
           f'--token {token} ' + \
           f'--node-name {name} ' + \
           f'{public_ip} {private_ip} ' + \
           f'{etcd} {controlplane} {worker}'
    return ' '.join(shlex.split(cmd))

def get_ssh_cmd(user, host, port=22, key='~/.ssh/id_rsa', cmd=None):
    cmd = cmd if cmd is not None else ''
    return f'ssh -p {port} -i {key} {user}@{host} {cmd}'

for host in args.nodes:
    docker_cmd = get_docker_cmd(manager=args.manager, token=args.rancher_token, public_ip=host, etcd=args.etcd, controlplane=args.controlplane, worker=args.worker)
    ssh_cmd = get_ssh_cmd(args.user, host, port=args.port, key=args.key.resolve(), cmd=docker_cmd)
    print(f'Provisioning {host}')
    proc = subprocess.run(shlex.split(ssh_cmd), capture_output=True, text=True)
    print(proc.stdout)
    print(proc.stderr)
    print('Success' if proc.returncode == 0 else 'Failure')