import os.path
import ConfigParser
import sys


class EnhancedConfigParser(ConfigParser.SafeConfigParser, object):

    SEC_GLOBAL = 'GLOBAL'

    def __init__(self, default_value=None, required_section_options=None, env_virable=None):
        # ConfigParser.SafeConfigParser.__init__(self)
        if required_section_options:
            self.required_section_options = required_section_options
            self.required_section_options["GLOBAL"] = []
        else:
            """
            key: the PREFIX of section name, not exactly matching
            value: the required option of the section
            """
            self.required_section_options = {"GLOBAL": []}
        self.optionxform = str # make is case sensitive
        super(EnhancedConfigParser, self).__init__(defaults=default_value)

    def __translate_env_variables(self):
        for section in self.sections():
            for option in self.options(section):
                self.set(section, option, os.path.expandvars(self.get(section, option)))

    def __validate(self):
        """validate the config file, there is no required section, but if required_section_options is defined,
        any section's prefix name matched the key name, this section should have the required options which defined by
        required_section_options
        """
        for key in self.required_section_options.keys():
            for section in self.sections():
                if section.startswith(key):
                    for required_option in self.required_section_options[key]:
                        if len(self.options_with_prefix(section, required_option)) == 0:
                            raise MissingRequiredOptionsException(
                                "Missing required option '%s' in section : [%s]" % (required_option, section))

    def __import_global_setting(self):
        """Merge global setting to all sections"""
        for section in self.sections():
            if section != 'GLOBAL':
                for option in self.options('GLOBAL'):
                    if not self.has_option(section, option):
                        value = self.get('GLOBAL', option)
                        self.set(section, option, value)

    def read(self, filename):
        if not os.path.isfile(filename):
            raise IOError("%s not found" % filename)
        super(EnhancedConfigParser, self).read(filename)
        self.__import_global_setting()
        self.__validate()
        self.__translate_env_variables()

    def sections_with_prefix(self, prefix):
        """Return a list of section names with specific prefix."""
        return [section for section in self.sections() if section.startswith(prefix)]

    def options_with_prefix(self, section, prefix):
        """Return a list of option names for the given section name with specific prefix."""
        return [option for option in self.options(section) if option.startswith(prefix)]

    def getlist(self, section, option):
        """get raw value as list, seperator: comma"""
        value = self.get(section, option)
        return [v.strip() for v in value.split(',')]

    def dump_config(self):
        for section in self.sections():
            print "[%s]" % section
            for option in self.options(section):
                print " ", option, "=", self.get(section, option)


class MissingRequiredOptionsException(Exception):
    pass


if __name__ == '__main__':

    # Init ERSConfigParser
    # required_section_options = {
    #     "GLOBAL": [],
    #     "APP": [],
    #     "LAMBDA": [],
    #     'CLOUDFORMATION': []
    # }
    ers_config_parser = EnhancedConfigParser()
    ers_config_parser.read(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
                                                        '../sample/cd_sample01.conf')))

    print ers_config_parser.sections_with_prefix('GLO')

    # Print out options with specific prefix in a section
    print ers_config_parser.options_with_prefix('APP-AMPS', 'app')

    # get option value as list
    # print ers_config_parser.getlist('APP01', 'app_01')
    # print ers_config_parser.getlist('LAMBDA', 'regions')

    ers_config_parser.dump_config()

    # Exception from sample02 which has no required options
    # ers_config_parser = ERSConfigParser(required_section_options)
    # ers_config_parser.read(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
    #                                                     '../Configs/sample/cd_sample02.conf')))

    # Exception from sample02 which has no required sections
    # ers_config_parser = ERSConfigParser(required_section_options)
    # ers_config_parser.read(os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]),
    #                                                     '../Configs/sample/cd_sample03.conf')))
