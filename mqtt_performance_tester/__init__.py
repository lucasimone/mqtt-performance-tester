import os
import shutil
import time
import errno
import logging
from configparser import ConfigParser

TMPDIR  = "tmp"
DATADIR = "data"
LOGDIR  = "log"
BACKUP  = "backup"
CFG_DIR = "cfg"

# generate dirs
for d in TMPDIR, DATADIR, LOGDIR, BACKUP:
    try:
        os.makedirs(d)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

LOG_FORMAT   = '%(levelname)-7s | %(asctime)s | %(name)40s:%(lineno)-3d| %(message)s'
LOG_FILENAME = "log/mqtt_performance.log"

# Configure Logger
logging.basicConfig(filename=LOG_FILENAME, level=logging.DEBUG, format=LOG_FORMAT)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT)

# Not used at the moment
fileHandler = logging.FileHandler(LOG_FILENAME, mode='w')
fileHandler.setFormatter(formatter)
fileHandler.setLevel(logging.DEBUG)

sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.propagate = True






def backup_data_folder():

    if os.path.exists(DATADIR):
        time_val = time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime(time.time()))

        old_data = '@'.join([DATADIR, time_val])
        os.rename(DATADIR, old_data)
        shutil.move(old_data, BACKUP)



def set_default_cfg():

    # add the settings to the structure of the file, and lets write it out...
    logger.info("Create the default configuration file...")

    # lets create that config file for next time...
    cfgfile = open("%s/mqtt_tester.ini"%CFG_DIR, 'w')

    Config = ConfigParser()
    Config.add_section('PATH')
    Config.set('PATH', 'TEST_RESULT', "data/report.txt")
    Config.set('PATH', 'FILENAME',    "data/mqtt_capture")

    Config.add_section('MQTT')
    Config.set('MQTT', 'PAYLOAD_LIST', "128, 256, 512, 1024, 1152, 1280")
    Config.set('MQTT', 'QoS', "1,2")
    Config.set('MQTT', 'N_PACKET_SEND', "1")
    Config.set('MQTT', 'TOPIC', "topic")

    Config.add_section('PING')
    Config.set('PING', 'GW_IP', "localhost")

    Config.add_section('SNIFFER')
    Config.set('SNIFFER', 'IFC', "lo0")
    Config.set('SNIFFER', "TCPDUMP_FILTER", "")

    Config.write(cfgfile)
    cfgfile.close()

    logger.info("Created file %s/mqtt_tester.ini..." % CFG_DIR)


def read_configuration():

    if not os.path.exists("%s/mqtt_tester.ini"%CFG_DIR):
        set_default_cfg()

    config = ConfigParser()
    config.read("%s/mqtt_tester.ini" % CFG_DIR)
    return config
