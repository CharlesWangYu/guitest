import pdb
import logging
import os
from configparser import ConfigParser

#pdb.set_trace()
logging.basicConfig(level = logging.DEBUG)

# Load and parser config file
config = ConfigParser()
config.read('testRrte.conf', encoding='UTF-8')

mode = config['MISC']['TEST_FILE_TYPE'].strip("'")
host = config['MISC']['HOST_APP_FILE'].strip("'")
menu = config['MISC']['INPUT_MENU_SPEC_FILE'].strip("'")
test = config['MISC']['TEST_FILE'].strip("'")
out  = config['MISC']['OUTPUT_PATH'].strip("'")

logging.debug('mode = %s' % mode)
logging.debug('host = %s' % host)
logging.debug('menu = %s' % menu)
logging.debug('test = %s' % test)
logging.debug('out = %s' % out)

# Startup RRTE and load target FDI package or EDD file
execCmd = '\"\"' + host + '\" -l \"' + test + '\"\"'
logging.debug('execCmd = %s' % execCmd)
os.system(execCmd)
