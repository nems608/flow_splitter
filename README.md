# Flow Splitter

This is a bash script for configuring networking and IPTables rules in order to turn a Linux system into a 'reverse load-balancer'. Outgoing TCP connections are source-NATed to a range of IP addresses in round-robin fashion. The idea is to distribute outgoing traffic over a range of IPs to simulate distributed traffic (DDoS simulation) or bypass Fail2Ban-style failed-login limits.

## Getting started

Just run the script to set up the system as a router. You must set the incoming interface IP yourself.

Usage: `./flow_splitter.sh dist_iface out_iface dest_net/cidr start_ip/cidr end_ip`

`dist_iface`: This is the outgoing interface for all distributed traffic.
`out_iface`: This is the outgoing interface for all non-distributed traffic (e.g. google.com).

`dest_net/cidr`: SNATing rules will only apply to traffic bound to this network.

`start_ip/cidr`: This is the first IP in the range to claim. `cidr` specifies the netmask for all claimed IPs

`end_ip`: This is the last IP in the range to claim.
