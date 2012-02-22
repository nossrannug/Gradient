from twisted.internet import reactor, protocol
import pickle

class Bootstrap(protocol.Protocol):
    def __init__(self):
	print "-----------------------------------"
        try:
		print "Smidur: ", self.factory.content
	except:
		print "Empty."
	#self.clients = {}
	#self.content = {}


    def connectionMade(self):
        print "connection from: ", self.transport.getPeer().host
        #self.clients.append(self.transport.getPeer().host)
	c = "%s:%d" % (self.transport.getPeer().host, self.transport.getPeer().port)
        self.factory.clients[c] = { "host" : self.transport.getPeer().host, "port" : self.transport.getPeer().port}
	print "On Connect: ", self.factory.content

    ### XXX hvad ef tengingin slitnar?


    def sendPickle(self, cmd, data):
	if cmd == 'M':
		print "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM"
	self.transport.write ("%c%s" % (cmd, pickle.dumps(data)))


    def recvPickle(self, data):
	try:
		obj = pickle.loads(data[1:])
		self.transport.write("TACK\n")
		self.transport.write("b")
		return obj
	except:
		print "Error parsing pickle command"
		self.transport.write("TERR\n")
		return None

   
    def sendNodes(self, c):
	# Send a list of relevant nodes to a particular client
	nodes = []
	print "bla"
	print "1: ", self.factory.clients[c]['interests']
	print "2: ", self.factory.content
	try:
		print "Content: ", self.factory.clients[c]['interests']
		nodes = self.factory.content[self.factory.clients[c]['interests']]		
	except:
		print "Content list is empty"
		#self.content[self.clients[c]['interests']] = []
	#print "Nodes: ", nodes
	self.sendPickle('L', nodes)
 
    def clientConnectTo(self, connectTo):
	self.sendPickle('M', connectTo)
	

    def dataReceived(self, data):
        #self.transport.write(data)
        #print "from: ", self.transport.getPeer().host,":",self.transport.getPeer().port, " : ", data
	# Protocol, 'T' means text, 'P' means pickle
	c = "%s:%d" % (self.transport.getPeer().host, self.transport.getPeer().port)
	if data[0] == 'T': # Text
		print "Text: ", data[1:]
	elif data[0] == "N":
		print "New client information. Port: ", self.transport.getPeer().port
		obj = self.recvPickle(data)
		# XXX error handling
		self.factory.clients[c]['inport'] = obj['inport']
		self.factory.clients[c]['rate'] = obj['rate']
	elif data[0] == "C": ## Content
		print "Client requesting content. Port: ", self.transport.getPeer().port
		obj = self.recvPickle(data)
		# XXX error handling
		self.factory.clients[c]['interests'] = obj['interests']
		print "Interests: ", self.factory.clients[c]['interests']
	elif data[0] == "G":
		print "Client wants a list of nodes. Port: ", self.transport.getPeer().port
		self.sendNodes(c)	
	elif data[0] == "O":
		print "Client offering content. Port: ", self.transport.getPeer().port
		self.factory.content[self.factory.clients[c]['interests']] = []
		self.factory.content[self.factory.clients[c]['interests']].append([self.transport.getPeer().host, self.factory.clients[c]['inport']])
		print "Content: ", self.factory.content
	elif data[0] == "R":
		print "Traceroute results from client"
		obj = self.recvPickle(data)
		# XXX
		# Add information to the graph
		# Construct tree from graph
		# Send information to client on where to connect to
		# connectTo = { 'ip' : ipAddress, 'port' : thePortNumber }
		# self.makeConnection(connectTo)

		# For now just send the last ip that connected
		self.connectTo = self.factory.content[self.factory.clients[c]['interests']][-1]
		print "Connect To: ", self.connectTo
	elif data[0] == 'M':	
		self.clientConnectTo(self.connectTo)
	else:
		self.transport.write("TNo such command\n")
		
	

class BootstrapFactory(protocol.Factory):
	def __init__(self):
		self.content = {}
		self.clients = {}
		print "asdfasdfasdfasdfasdfasdfasfdds"

	def buildProtocol(self, addr):
		factory = Bootstrap()
		print "-------------------------"
		print "protocol factory."
		print "-------------------------"
		factory.factory = self 
		return factory
		

if __name__ == "__main__":
	bootstrapPort = 8007
	factory = BootstrapFactory()
	reactor.listenTCP(bootstrapPort, factory)
	reactor.run()
