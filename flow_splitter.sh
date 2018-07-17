#!/bin/bash
dest_net="192.168.2.0/24"
num_ips=2
dev="eth1"

help_text() {
    echo "Usage: ./flow_splitter.sh interface dest_net start_ip/cidr end_ip"
    echo "For example: ./flow_splitter eth1 10.10.0.0/24 192.168.1.5/16 192.168.150.255"
    return 1
}

parse_arguments() {
    if [ "$1" == "" ]; then
        help_text
        exit
    fi
    dev="$1"
    if [ "$2" == "" ]; then
        help_text
        exit
    fi
    dest_net="$2"
    if [ "$3" == "" ]; then
        help_text
        exit
    fi
    start_ip=$(echo "$3" | cut -d '/' -f 1)
    netmask=$(echo "$3" | cut -d '/' -f 2)
    if [ "$4" == "" ]; then
        help_text
        exit
    fi
    end_ip="$4"
}

increment_ip() {
    old_ip="$1"
    oct1=$(echo $old_ip | cut -d '.' -f 1)
    oct2=$(echo $old_ip | cut -d '.' -f 2)
    oct3=$(echo $old_ip | cut -d '.' -f 3)
    oct4=$(echo $old_ip | cut -d '.' -f 4)
    oct4=$(($oct4 + 1 % 255))
    if [ $oct4 == 0 ]; then
        oct3=$(($oct3 + 1 % 255))
        if [ $oct3 == 0 ]; then
            oct2=$(($oct2 + 1 % 255))
            if [ $oct2 == 0 ]; then
                oct1=$(($oct1 + 1 % 255))
            fi
        fi
     fi
     ip="$oct1"."$oct2"."$oct3"."$oct4"
}

enable_ip_fowarding() {
    sed -i 's/^.*net.ipv4.ip_forward.*$/net.ipv4.ip_forward=1/' /etc/sysctl.conf
    sysctl -p /etc/sysctl.conf
}

claim_ips() {
    ip address flush $dev
    ip link set dev $dev up
    
    ip="$start_ip"
    while [[ "$end_ip" > "$ip" || "$end_ip" == "$ip" ]]; do
        ip address add $ip/$netmask dev $dev
        increment_ip $ip
    done
}

setup_snat() {
    shared_opts="-t nat -I POSTROUTING 1 -o $dev -p tcp -d $dest_net -m state --state NEW -m statistic --mode nth"
    iptables -t nat -F 
  
    every=1
    ip="$start_ip"
    while [[ "$end_ip" > "$ip" || "$end_ip" == "$ip" ]]; do
        echo $ip $end_ip
        iptables $shared_opts --every $every --packet 0 -j SNAT --to $ip
        increment_ip $ip
        every=$(($every + 1))
    done
}

parse_arguments $@
enable_ip_fowarding
claim_ips
setup_snat
