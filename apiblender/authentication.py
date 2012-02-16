class AuthenticationManager:
	"""Ensure authentication."""

	def __init__(self):
		self.servers_status = {}


	def add_server(self, server):
		if server.name not in self.servers_status:
			parameters = server.authentication.request_parameters(server.host)
			if parameters:
				self.servers_status.update({ server.name: {
												"parameters": parameters} })
			else:
				print 'ERROR: could not auth'
