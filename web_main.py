# -*- coding: utf-8 -*-
from flask import Flask
import subprocess, sys
import ConfigParser
from flask import request
import json
import os


app = Flask(__name__)
app_root = os.getcwd()
config = ConfigParser.ConfigParser()
config.optionxform=str

cmd_template = {
    'run': "python cc_main.py -c config/{0}.conf -a {1}",
    'quest_query': "scripts/find_quest.py -n {0}"
}

def __dump_config():
    for section in config.sections():
        print "[%s]" % section
        for option in config.options(section):
            print " ", option, "=", config.get(section, option)

def run_command(cmd, cwd=os.getcwd()):
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
    stdout, stderr = process.communicate()
    return stdout

@app.route("/show_setting/<user>/<section>", methods=['POST'])
def show(user, section):
    config_path = os.path.join(app_root, 'config', '{0}.conf'.format(user))
    config.read(config_path)
    if section != 'ALL':
        content = '[{0}]\n'.format(section)
        content += '\n'.join(['{0}={1}'.format(option, config.get(section, option))for option in config.options(section)])
        return content
    else:
        content = ''
        for section in config.sections():
            content += '\n\n[{0}]\n'.format(section)
            content += '\n'.join(['{0}={1}'.format(option, config.get(section, option))for option in config.options(section)])
        return content

@app.route("/set/<user>/<section>", methods=['POST'])
def set(user, section):
    data = request.json
    print data
    config_path = os.path.join(app_root, 'config', '{0}.conf'.format(user))
    print config_path
    config.read(config_path)
    #__dump_config()
    for k, v in data.iteritems():
        print 'set {0} to {1} in section [{2}]'.format(k, v, section)
        config.set(section, k, v)
    with open(config_path, 'wb') as configfile:
        config.write(configfile)
    return u'設定檔已儲存'

@app.route("/run/<user>/<section>", methods=['POST'])
def run(user, section):
    try:
        cmd = cmd_template['run'].format(user, section)
        print cmd
        result = run_command(cmd)
        return result
    except Exception as e:
        return e

@app.route('/quest_query/<quest_name>', methods=['POST'])
def quest_query(quest_name):
    try:
        cmd = cmd_template['quest_query'].format(quest_name)
        print cmd
        result = run_command(cmd)
        return result
    except Exception as e:
        return e



if __name__ == "__main__":
    app.run('0.0.0.0', port=80)
