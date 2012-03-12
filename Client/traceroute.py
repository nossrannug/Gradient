class Traceroute:
	def __init__(self):
		pass

	def runTraceroute(self, nodes):
		# nodes is a list containing IP's ["###.###.###.###", "###.###.###.###"]
		# return the best, the ones that are closest
		
		# Currently getss random 5 items from nodes, applies a random weight to each
		# item and returns
		import random
		nodes = random.sample(nodes, 5)

		result = []
		for n in nodes:
			result.append([n, random.randint(0,100)])

		return result

if __name__ == "__main__":
	l = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
	print Traceroute().runTraceroute(l)
