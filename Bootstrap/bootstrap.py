from twisted.internet import reactor, protocol
import pickle

class Bootstrap(protocol.Protocol):
    def __init__(self):
        self.clients = {}
	self.content = {}


    def connectionMade(self):
        print "connection from: ", self.transport.getPeer().host
        #self.clients.append(self.transport.getPeer().host)
	c = "%s:%d" % (self.transport.getPeer().host, self.transport.getPeer().port)
        self.clients[c] = { "host" : self.transport.getPeer().host, "port" : self.transport.getPeer().port}

    ### XXX hvad ef tengingin slitnar?


    def sendPickle(self, cmd, data):
	self.transport.write ("%c%s" % (cmd, pickle.dumps(data)))


    def recvPickle(self, data):
	try:
		obj = pickle.loads(data[1:])
		self.transport.write("TACK\n")
		return obj
	except:
		print "Error parsing pickle command"
		self.transport.write("TERR\n")
		return None

   
    def sendNodes(self, c):
	# Send a list of relevant nodes to a particular client
	nodes = []
	try:
		nodes = self.content[self.clients[c]['interests']]		
	except:
		self.content[self.clients[c]['interests']] = []
	#print "Nodes: ", nodes
	self.sendPickle('L', nodes)
 

    def dataReceived(self, data):
        #self.transport.write(data)
        #print "from: ", self.transport.getPeer().host,":",self.transport.getPeer().port, " : ", data
	# Protocol, 'T' means text, 'P' means pickle
	c = "%s:%d" % (self.transport.getPeer().host, self.transport.getPeer().port)
	if data[0] == 'T': # Text
		print "Text: ", data[1:]
	elif data[0] == "N":
		obj = self.recvPickle(data)
		# XXX error handling
		self.clients[c]['inport'] = obj['inport']
		self.clients[c]['rate'] = obj['rate']
	elif data[0] == "C": ## Content
		obj = self.recvPickle(data)
		# XXX error handling
		self.clients[c]['interests'] = obj['interests']
		print "Interests: ", self.clients[c]['interests']
	elif data[0] == "G":
		# Client wants a list of nodes
		self.sendNodes(c)	
	elif data[0] == "O":
		self.content[self.clients[c]['interests']] = []
		self.content[self.clients[c]['interests']].append([self.transport.getPeer().host, self.clients[c]['inport']])
		print "Content: ", self.content
	elif data[0] == "R":
		# Traceroute results from client
		obj = self.recvPickle(data)
		# XXX
		# Add information to the graph
		# Construct tree from graph
		# Send information to client on where to connect to
		# connectTo = { 'ip' : ipAddress, 'port' : thePortNumber }
		# self.makeConnection(connectTo)

		# For now just send the last ip that connected
		connectTo = self.content[self.clients[c]['interests']][-1]
		print "Connect To: ", connectTo
	else:
		self.transport.write("TNo such command\n")
		
	


bootstrapPort = 8007
factory = protocol.ServerFactory()
factory.protocol = Bootstrap
reactor.listenTCP(bootstrapPort, factory)
reactor.run()
