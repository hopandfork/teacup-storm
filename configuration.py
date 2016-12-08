import yaml

''' Global configuration object. '''
global config

class Configuration:
    def __init__(self):
        conf = self.parse_configuration_file('config.yaml')

        self.get_required_parameter(conf, 'aws_access_key_id')
        self.get_required_parameter(conf, 'aws_secret_access_key')
        self.get_required_parameter(conf, 'region_name')
        self.get_required_parameter(conf, 'key_pair')
        self.get_required_parameter(conf, 'security_groups_zk')
        self.get_required_parameter(conf, 'security_groups_ui')
        self.get_required_parameter(conf, 'security_groups_ni')
        self.get_required_parameter(conf, 'security_groups_sv')
        self.get_parameter(conf, 'zk_instances', 1)
        
    def parse_configuration_file(self, config_file):
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

    def get_required_parameter(self, conf, key):
        if key in conf:
            setattr(self, key, conf[key])
        else:
            print("Missing required parameter '{}' in configuration."
                    .format(key))

    def get_parameter(self, conf, key, default_value):
        if key in conf:
            setattr(self, key, conf[key])
        else:
            setattr(self, key, default_value)