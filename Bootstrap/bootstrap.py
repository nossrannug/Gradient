from twisted.internet import reactor, protocol
import pickle

class Bootstrap(protocol.Protocol):
    def __init__(self):
        self.clients = {}

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
		print obj
		self.transport.write("TACK\n")
		return obj
	except:
		print "Error parsing pickle command"
		self.transport.write("TERR\n")
		return None
   
    def sendNodes(self, c):
	# Send a list of relevant nodes to a particular client
	self.sendPickle('L', [ "192.168.1.1", "192.168.1.2" ])
 
    def dataReceived(self, data):
        #self.transport.write(data)
        #print "from: ", self.transport.getPeer().host,":",self.transport.getPeer().port, " : ", data
	# Protocol, 'T' means text, 'P' means pickle
	c = "%s:%d" % (self.transport.getPeer().host, self.transport.getPeer().port)
	if data[0] == 'T': # Text
		print data[1:]
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
		obj = self.recvPickle(data)
		# Client wants a list of nodes
		self.sendNodes (c)	
	else:
		self.transport.write("TNo such command\n")
		
	


bootstrapPort = 8007
factory = protocol.ServerFactory()
factory.protocol = Bootstrap
reactor.listenTCP(bootstrapPort, factory)
reactor.run()
