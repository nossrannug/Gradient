from twisted.internet import reactor, protocol

class Bootstrap(protocol.Protocol):
    def __init__(self):
        self.clients = []

    def connectionMade(self):
        print "connection from: ", self.transport.getPeer().host
        self.clients.append(self.transport.getPeer().host)
                
    def dataReceived(self, data):
        #self.transport.write(data)
        print "from: ", self.transport.getPeer().host,":",self.transport.getPeer().port, " : ", data


bootstrapPort = 8007
factory = protocol.ServerFactory()
factory.protocol = Bootstrap
reactor.listenTCP(bootstrapPort, factory)
reactor.run()
