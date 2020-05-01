#!/usr/bin/python

"""
linuxrouter.py: Example network with Linux IP router

This example converts a Node into a router using IP forwarding
already built into Linux.

The example topology creates a router and three IP subnets:

    - 192.168.1.0/24 (r0-eth1, IP: 192.168.1.1)
    - 172.16.0.0/12 (r0-eth2, IP: 172.16.0.1)
    - 10.0.0.0/8 (r0-eth3, IP: 10.0.0.1)

Each subnet consists of a single host connected to
a single switch:

    r0-eth1 - s1-eth1 - h1-eth0 (IP: 192.168.1.100)
    r0-eth2 - s2-eth1 - h2-eth0 (IP: 172.16.0.100)
    r0-eth3 - s3-eth1 - h3-eth0 (IP: 10.0.0.100)

The example relies on default routing entries that are
automatically created for each router interface, as well
as 'defaultRoute' parameters for the host interfaces.

Additional routes may be added to the router or hosts by
executing 'ip route' or 'route' commands on the router or hosts.
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):

        defaultIP = '10.0.0.1/24'  # IP address for r0-eth1
        router0 = self.addNode( 'r0', cls=LinuxRouter, ip=defaultIP )
        router1 = self.addNode( 'r1', cls=LinuxRouter, ip='10.0.1.1/24')

        s1, s2, s3, s4 = [ self.addSwitch( s ) for s in ( 's1', 's2', 's3', 's4' ) ]

        self.addLink( s1, router0, intfName2='r0-eth1',
                      params2={ 'ip' : defaultIP } )  # for clarity
        self.addLink( s2, router0, intfName2='r0-eth2',
                      params2={ 'ip' : '10.0.2.1/24' } )
        self.addLink( s3, router1, intfName2='r1-eth1',
                      params2={ 'ip' : '10.0.1.1/24' })
        self.addLink( s4, router1, intfName2='r1-eth2',
                      params2={ 'ip' : '10.0.3.1/24' })

        h1 = self.addHost( 'h1', ip='10.0.0.100/24',
                           defaultRoute='via 10.0.0.1' )
        h2 = self.addHost( 'h2', ip='10.0.2.100/24',
                           defaultRoute='via 10.0.2.1' )

        self.addLink( s1, h1, intfName2='h1-eth0')
        self.addLink( s2, h2, intfName2='h2-eth0')
        self.addLink( s3, h1, intfName2='h1-eth1',
                      params2={ 'ip' : '10.0.1.100/24' })
        self.addLink( s4, h2, intfName2='h2-eth1',
                      params2={ 'ip' : '10.0.3.100/24' })

        #for h, s in [ (h1, s1), (h2, s2) ]:
        #    self.addLink( h, s )


def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()
    info( '*** Routing Table on Router:\n' )
    info( net[ 'r0' ].cmd( 'route' ) )
    info( net[ 'h2' ].cmd( 'nohup python -m SimpleHTTPServer 80 &' ))
    info( net[ 'h1' ].cmd( 'wget http://10.0.2.100/ubuntu-18.04.4-live-server-amd64.iso' ))
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
