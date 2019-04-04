
#arreglar este codigo para iniciar multiples instancias de UDP

from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
import parameters as PARAM

class UDPFactory(DatagramProtocol):
    def datagramReceived(self, data, addr):
        print("received %r from %s:%d" % (data, addr[0], addr[1]))


def init():
    reactor.listenUDP(PARAM.SOCKET_UDP_PORT, UDPFactory())
    reactor.run()

init()