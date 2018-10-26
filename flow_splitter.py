#!/usr/bin/python3
import sys
import subprocess
import ipaddress

def help_text():
    print("Usage: ./flow_splitter.sh dist_iface out_iface dest_net start_ip/cidr end_ip")
    print("For example: ./flow_splitter eth1 eth2 10.10.0.0/24 192.168.1.5/16 192.168.150.255")
    exit(1)

def parse_arguments():
    dist_dev = sys.argv[1]
    out_dev = sys.argv[2]
    dest_net= sys.argv[3]
    start_ip= sys.argv[4].split('/')[0]
    netmask = sys.argv[4].split('/')[1]
    end_ip = sys.argv[5]
    end_ip = ipaddress.ip_address(end_ip)
    return dist_dev, out_dev, dest_net, start_ip, netmask, end_ip

def enable_ip_fowarding():
    cmd = "sed -i 's/^.*net.ipv4.ip_forward.*$/net.ipv4.ip_forward=1/' /etc/sysctl.conf"
    print(cmd)
    #subprocess.call(cmd, shell=True)
    cmd = 'sysctl -p /etc/sysctl.conf'
    print(cmd)
    #subprocess.call(cmd, shell=True)

def claim_ips(dist_dev, start_ip, netmask, end_ip):
    cmd = 'ip address flush {}'.format(dist_dev)
    print(cmd)
    #subprocess.call(cmd, shell=True)
    print(cmd)
    cmd = 'ip link set dev {} up'.format(dist_dev)
    #subprocess.call(cmd, shell=True)
    
    ip = ipaddress.ip_address(start_ip)
    while end_ip >= ip:
        cmd = 'ip address add {}/{} dev {}'.format(ip, netmask, dist_dev)
        print(cmd)
        #subprocess.call(cmd, shell=True)
        ip += 1

def setup_snat(dist_dev, dest_net, start_ip, end_ip, out_dev):
    shared_opts='-t nat -I POSTROUTING 1 -o {} -p tcp -d {} -m state --state NEW -m statistic --mode nth'.format(dist_dev, dest_net)
    cmd = 'iptables -t nat -F'
    print(cmd)
    #subprocess.call(cmd, shell=True)
  
    every = 1
    ip = ipaddress.ip_address(start_ip)
    while end_ip >= ip:
        cmd = 'iptables {} --every {} --packet 0 -j SNAT --to {}'.format(shared_opts, every, ip)
        print(cmd)
        #subprocess.call(cmd, shell=True)
        ip += 1
        every += 1
    cmd = 'iptables -t nat -A POSTROUTING -o {} -j MASQUERADE'.format(out_dev)
    print(cmd)
    #subprocess.call(cmd, shell=True)

if __name__ == '__main__':
    if len(sys.argv) != 6:
        help_text()
    dist_dev, out_dev, dest_net, start_ip, netmask, end_ip = parse_arguments()
    enable_ip_fowarding()
    claim_ips(dist_dev, start_ip, netmask, end_ip)
    setup_snat(dist_dev, dest_net, start_ip, end_ip, out_dev)
