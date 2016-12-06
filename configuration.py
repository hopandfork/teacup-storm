import yaml

''' Global configuration object. '''
global config

class Configuration:
    def __init__(self):
        conf = self.parseConfigurationFile('config.yaml')

        self.getRequiredParameter(conf, 'aws_access_key_id')
        self.getRequiredParameter(conf, 'aws_secret_access_key')
        self.getRequiredParameter(conf, 'region_name')
        self.getRequiredParameter(conf, 'key_pair')
        self.getRequiredParameter(conf, 'security_groups_zk')
        self.getRequiredParameter(conf, 'security_groups_ui')
        self.getRequiredParameter(conf, 'security_groups_ni')
        self.getRequiredParameter(conf, 'security_groups_sv')
        self.getParameter(conf, 'zk_instances', 1)
        
    def parseConfigurationFile (self, config_file):
        try:
            stream = open(config_file)
            conf = yaml.load(stream)
            if conf == None:
                raise yaml.YAMLError
            stream.close()
        except IOError:
            print("Failed to open configuration file '{}'".format(config_file))
            exit(1)
        except yaml.YAMLError:
            print("Error in configuration file '{}'".format(config_file))
            stream.close()
            exit(2)
        else:
            return conf

    def getRequiredParameter(self, conf, key):
        if key in conf:
            setattr(self, key, conf[key])
        else:
            print("Missing required parameter '{}' in configuration."
                    .format(key))
            exit(2)

    def getParameter(self, conf, key, defaultValue):
        if key in conf:
            setattr(self, key, conf[key])
        else:
            setattr(self, key, defaultValue)

        
    
if __name__ == "__main__":
    print("You should NOT run this file!")
