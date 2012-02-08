from twisted.internet import protocol, reactor
import os
import pickle

class Client(protocol.Protocol):
    STATE_INITIAL = 1
    STATE_SENT_N = 2
    STATE_SENT_C = 3
    STATE_SENT_G = 4

    def __init__(self):
        self.connectTo = ""
	self.state = self.STATE_INITIAL


    def sendContent(self):
   	# Protocol: Step 1: Send information about self
	me = { "interests" : [ "red little riding hood", "vertigo" ] }
	self.transport.write ("C%s" % (pickle.dumps(me)))
 
    def sendNew(self):
	# Protocol: Step 1: Send information about self
	me = { "inport" : "1234", "pid" : str(os.getpid()), "rate" : [ 1,2,3,4] }
	self.transport.write ("N%s" % (pickle.dumps(me)))
	
    def sendGetNodes(self):
	# Protocol: Step 1: Send information about self
	self.transport.write ("G")
	
    def dataReceived(self, data):
        self.connectTo = data

	#print "from: ", self.transport.getPeer().host,":",self.transport.getPeer().port, " : ", data
	# Protocol, 'T' means text, 'P' means pickle
	if data[0] == 'T': # Text
		if data[1:4] == "ACK": # Success
			if self.state == self.STATE_SENT_N:
				self.sendContent()
				self.state = self.STATE_SENT_C

			if self.state == self.STATE_SENT_C:
				self.sendGetNodes()
				self.state = self.STATE_SENT_G

		print data[1:]
	elif data[0] == 'L': ## List of nodes
		try:
			obj = pickle.loads(data[1:])
			print obj
			# XXX: do something with the object
			#self.transport.write("TACK\n")
		except:
			print "Error parsing pickle command"
			self.transport.write("TERR\n")
	else:
		self.transport.write("TUnknown response\n")
	
        print data
       
    def connectionMade(self):
    	self.sendNew()
	self.state = self.STATE_SENT_N


 

bootstrap = "localhost"
bootstrapPort = 8007
factory = protocol.ClientFactory()
factory.protocol = Client
reactor.connectTCP(bootstrap, bootstrapPort, factory)
reactor.run()
