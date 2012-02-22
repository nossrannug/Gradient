from twisted.internet import protocol, reactor
import os, sys
import pickle
from clientcontent import ClientSendReceiveFactory

class Client(protocol.Protocol):
    STATE_INITIAL = 1
    STATE_SENT_N = 2
    STATE_SENT_C = 3
    STATE_SENT_G = 4
    STATE_SENT_R = 5
    STATE_SENT_M = 6
    STATE_SENT_O = 10
    def __init__(self, port):
        self.connectTo = {}
	self.state = self.STATE_INITIAL
	self.port = port

    def sendNew(self):
	# Protocol: Step 1: Send information about self
	print "Send information about self to bootstrap."
	me = { "inport" : self.port, "pid" : str(os.getpid()), "rate" : 100 }
	self.sendPickle('N', me)

    def sendContent(self):
	print "Request content from bootstrap."
   	# Protocol: Step 2: Send information about what content is requested
	me = { "interests" : "livestream" }
	self.sendPickle('C', me)
 
    def sendGetNodes(self):
	print "Request nodes from bootstrap."
	# Protocol: Step 3: Request nodes offering content
	self.transport.write ("G")

    def sendOfferContent(self):
	print "Offer content to bootstrap."
	# Protocol: Step ?: If there are no nodes offering content
	# being offering live stream
	self.transport.write("O")
	self.connectToContent(None)

    def tracerouteNodes(self, nodes):
	print "Run traceroute on all nodes."
	# traceroute nodes
	return None

    def sendTracerouteResult(self, result):
	print "Send traceroute result to bootstrap."
	self.sendPickle('R', result)	

    # Havn't tested if this works or not
    def connectToContent(self, connectTo):
	if connectTo != None:
		print "Connecting to: ", connectTo
		reactor.connectTCP(connectTo[0], connectTo[1], ClientSendReceiveFactory())
	else:
		print "Listening on port: ", self.port
		reactor.listenTCP(self.port, ClientSendReceiveFactory())

    def sendGetConnectToAddress(self):
	self.transport.write('M')

    def sendPickle(self, cmd, data):
	self.transport.write("%c%s" % (cmd, pickle.dumps(data)))

    def recvPickle(self, data):
	#print "Data: ", data
	#print "State: ", self.state
	try:
		obj = pickle.loads(data[1:])
		#print obj
		#self.transport.write("TACK\n")
		return obj
	except:
		print "Error parsing pickle command"
		self.transport.write("TERR\n")
		return None

    def dataReceived(self, data):
        self.connectTo = data
	print data[0]
	# Protocol, 'T' means text, 'P' means pickle
	if data[0] == 'T': # Text
		if data[1:4] == "ACK": # Success
			if self.state == self.STATE_SENT_N:
				self.sendContent()
				self.state = self.STATE_SENT_C

			elif self.state == self.STATE_SENT_C:
				self.sendGetNodes()
				self.state = self.STATE_SENT_G
			elif self.state == self.STATE_SENT_R:
				self.state == self.STATE_SENT_M
				self.sendGetConnectAddress()

		#print data[1:]
	elif data[0] == 'L': ## List of nodes
		# If no one is offering said content the client will start offering it
		obj = self.recvPickle(data)
		# Will just be a live video stream from web cam?
		print "List: ", obj
		if len(obj) == 0:
			self.sendOfferContent()
			self.state = self.STATE_SENT_O
			# XXX: write a class to start streaming something?
		else:
			# XXX: Tracerout to all nodes and send result to bootstrap
			result = self.tracerouteNodes(obj)
			self.sendTracerouteResult(result)
		# XXX: do something with the object
		#self.transport.write("TACK\n")
	elif data[0] == 'M':
		obj = self.recvPickle(data)
		print "Client needs to connect to: ", obj
		self.connectToContent(connectTo)
	else:
		self.transport.write("TUnknown response\n")
	
       
    def connectionMade(self):
    	self.sendNew()
	self.state = self.STATE_SENT_N


class ClientFactory(protocol.ClientFactory):
	def __init__(self, port):
		self.port = int(port)

	def buildProtocol(self, addr):
		protocol = Client(self.port)
		return protocol

	def clientConnectionFailed(self, connector, reasone):
		print "connection failed", connector
		

if __name__ == "__main__":
	bootstrapIP = "localhost"
	bootstrapPort = 8007
	factory = ClientFactory(sys.argv[1])
	reactor.connectTCP( bootstrapIP, bootstrapPort, factory)
	reactor.run()
