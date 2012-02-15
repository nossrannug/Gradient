from twisted.internet import protocol, reactor

class ClientSendReceiveFactory(protocol.Factory):
	def __inti__(self):
		self.echoers = []

	def buildProtocol(self, addr):
		return ClientSendReceive(self)


class ClientSendReceive(protocol.Protocol):
	def __inti__(self, factory):
		self.factory = factory

	# Need to test if this is just for incoming connections
	# or if it allso applies to connections that this client makes
	def connectionMade(self):
		print "Connection from: ", self.transport.getPeer().host
		self.factory.echoers.append(self)

	def dataReceived(self, data):
		print data
		for echoer in self.factory.echoers:
			eachoer.transport.write(data)

	def connectionLost(self, reason):
		self.factory.echoers.remove(self)


