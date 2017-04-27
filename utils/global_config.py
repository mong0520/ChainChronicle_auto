import ConfigParser
import enhanced_config_parser
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config', 'global.conf')

config = enhanced_config_parser.EnhancedConfigParser()
config.read(CONFIG_PATH)
host = config.get('GLOBAL', 'host')

def get_hostname():
    return host

def get_fqdn():
    return host.replace('http://', '')

if __name__ == '__main__':
    hostname = get_hostname()
    fqdn = get_fqdn()
    print hostname
    print fqdn

