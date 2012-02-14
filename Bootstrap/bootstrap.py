from twisted.internet import protocol, reactor

class Bootstrap(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

factory = protocol.ServerFactory()
factory.protocol = Bootstrap
reactor.listenTCP(8007, factory)
reactor.run()
