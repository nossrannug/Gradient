from twisted.internet import protocol, reactor

class ClientSendReceiveFactory(protocol.Factory):
	def __init__(self):
		self.echoers = []

	def buildProtocol(self, addr):
		csr = ClientSendReceive()
		csr.factory = self
		return csr


class ClientSendReceive(protocol.Protocol):
	def __init__(self):
		#self.factory = factory
		pass
	# Need to test if this is just for incoming connections
	# or if it allso applies to connections that this client makes
	def connectionMade(self):
		try:
			print "Connection from: ", self.transport.getPeer().host
			self.factory.echoers.append(self)
		except:
			print "Error in ClientSendReceive - connectionMade()"
	def dataReceived(self, data):
		print data
		for echoer in self.factory.echoers:
			echoer.transport.write(data)

	def connectionLost(self, reason):
		try:
			self.factory.echoers.remove(self)
		except:
			print "Error in ClientSendReceive - connectionLost()"


