from twisted.internet import protocol, reactor
import os
import pickle

class Client(protocol.Protocol):
    STATE_INITIAL = 1
    STATE_SENT_N = 2
    STATE_SENT_C = 3
    STATE_SENT_G = 4
    STATE_SENT_R = 5
    STATE_SENT_O = 10
    def __init__(self):
        self.connectTo = {}
	self.state = self.STATE_INITIAL

    def sendNew(self):
	# Protocol: Step 1: Send information about self
	me = { "inport" : "1234", "pid" : str(os.getpid()), "rate" : 100 }
	self.sendPickle('N', me)

    def sendContent(self):
   	# Protocol: Step 2: Send information about what content is requested
	me = { "interests" : "livestream" }
	self.sendPickle('C', me)
 
    def sendGetNodes(self):
	# Protocol: Step 3: Request nodes offering content
	self.transport.write ("G")

    def sendOfferContent(self):
	# Protocol: Step ?: If there are no nodes offering content
	# being offering live stream
	self.transport.write("O")

    def selfTracerouteNodes(self, nodes):
	# traceroute nodes
	return None

    def sendTracerouteResult(self, result):
	self.sendPickle('R', result)	

    def sendPickle(self, cmd, data):
	self.transport.write("%c%s" % (cmd, pickle.dumps(data)))

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

    def dataReceived(self, data):
        self.connectTo = data

	# Protocol, 'T' means text, 'P' means pickle
	if data[0] == 'T': # Text
		if data[1:4] == "ACK": # Success
			if self.state == self.STATE_SENT_N:
				self.sendContent()
				self.state = self.STATE_SENT_C

			elif self.state == self.STATE_SENT_C:
				self.sendGetNodes()
				self.state = self.STATE_SENT_G

		print data[1:]
	elif data[0] == 'L': ## List of nodes
		try:
			obj = pickle.loads(data[1:])
			# If no one is offering said content the client will start offering it
			# Will just be a live video stream from web cam?
			if len(obj) == 0:
				self.sendOfferContent()
				self.state = STATE_SENT_O
				# XXX: write a class to start streaming something?
			else:
				# XXX: Tracerout to all nodes and send result to bootstrap
				result = self.tracerouteNodes(obj)
				self.sendTracerouteResult(result)
			print obj
			# XXX: do something with the object
			#self.transport.write("TACK\n")
		except:
			print "Error parsing pickle command"
			self.transport.write("TERR\n")
	else:
		self.transport.write("TUnknown response\n")
	
       
    def connectionMade(self):
    	self.sendNew()
	self.state = self.STATE_SENT_N


 

bootstrap = "localhost"
bootstrapPort = 8007
factory = protocol.ClientFactory()
factory.protocol = Client
reactor.connectTCP(bootstrap, bootstrapPort, factory)
reactor.run()
