from twisted.internet import protocol, reactor

class Client(protocol.Protocol):
    def __init__(self):
        self.connectTo = ""

    def dataReceived(self, data):
        self.connectTo = data
        print data
        

bootstrap = "localhost"
bootstrapPort = 8007
factory = protocol.ClientFactory()
factory.protocol = Client
reactor.connectTCP(bootstrap, bootstrapPort, factory)
reactor.run()
