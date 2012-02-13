from twisted.internet import protocol, reactor
import threading

class ClientContent(threading.Thread):
	def __init__(self, connectTo):
		self.connectTo = connectTo
		threading.Thread.__init__(self)

	def run(self):
		# If connectTo not empty we want to connect to that host
		if self.connectTo != None:
			reactor.connectTCP(self.connectTo['ip'], self.connectTo['port'], ClientSendReceiveFactory())
		# We also want to be listening for incoming connections	
		reacotor.listenTCP('1234', self.factory)
		reactor.run()

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
		self.factory.echoers.append(self)

	def dataReceived(self, data):
		print data
		for echoer in self.factory.echoers:
			eachoer.transport.write(data)

	def connectionLost(self, reason):
		self.factory.echoers.remove(self)


