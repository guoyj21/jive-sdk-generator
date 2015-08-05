from pystache import TemplateSpec

class Pom(TemplateSpec):
    def __init__(self, data):
	self.groupId = data["groupId"]
	self.artifactId = data["artifactId"]
	self.version = data["version"]
	self.name = data["name"]
	self.clienturl = data["clienturl"]
	self.port = data["port"]
	self.appContext = data["appContext"]

    def groupId(self):
        return self.groupId

    def artifactId(self):
	return self.artifactid
    
    def version(self):
	return self.version

    def name(self):
	return self.name

    def clienturl(self):
        return self.clienturl

    def port(self):
	return self.port

    def appContext(self):
	return self.appContext
