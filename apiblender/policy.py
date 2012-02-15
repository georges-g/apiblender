# TODO: waiting time

class PolicyManager:

	""" Limit request when needed """

	def __init__(self):
		self.servers_status = {}


	def add_server(self, server):
		if server.name not in self.servers_status:
			self.servers_status.update({ server.name: {
																			"request_count": 0, 
																			"sleeping_state": False,
																			"sleeping_since": None } })
		

	def signal_server_request(self, server):
		self.servers_status[server.name]["request_count"] += 1

	
	def get_server_request_count(self, server):
		return self.servers_status[server.name]["request_count"]


	def get_request_permission(self, server):

		if self.servers_status[server.name]["sleeping_state"]:
			return False

		elif (self.servers_status[server.name]["request_count"]
					> server.policy.requests_per_hour):
			self.servers_status[server.name]["sleeping_state"] = True
			self.counters[host]["sleeping_since"] = datetime.now()
			return False

		else:
			return True


	def get_sleeping_time(self, server):
		if not self.servers_status[server.name]["sleeping_state"]:
			return 0
		else:
			date_diff = (datetime.now() - self.servers_status[server.name]["sleeping_state"])
			return (3600 - date_diff.total_seconds())
	

	def reset_server_sleep(self, server):
		self.servers_status[server.name]["sleeping_state"] = False
		self.servers_status[server.name]["sleeping_since"] = None 

