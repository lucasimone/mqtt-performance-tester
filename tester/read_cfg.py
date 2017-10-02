# CONFIGURATION_FILE = "mqtt_tester.ini"
# SECTION_PATH = "PATH"
# SECTION_MQTT = "MQTT"
# SECTION_PING = "PING"
# SECTION_SNIFFER = "SNIFFER"
#
# conf_ready = False
#
#
#
#
# if not os.path.exists('../mqtt_tester.ini'):
#
#     print("Set Default value into configuration file")
#     FILENAME = "data/mqtt_capture"
#     TMPDIR = "tmp"
#     DATADIR = "data"
#     LOGDIR = "log"
#     BACKUP = "backup"
#
#     TEST_RESULT= "data/report.txt"
#     #PAYLOAD_LIST = [128, 256, 512, 1024]
#     PAYLOAD_LIST = [128]
#     QoS = [1, 2]
#     N_PACKET_SEND = 100
#     TOPIC = 'topic'
#
#     IFC = "lo0"
#     GW_IP = "localhost"
#     TCPDUMP_FILTER =  '' # keep this empty or put ICMP + TCP
#
#     with open(CONFIGURATION_FILE, 'w') as configfile:
#         config = configparser.ConfigParser()
#         config.write(configfile)
#     conf_ready = True
#
# elif conf_ready == False:
#
#     print("Read configuration file")
#     config = configparser.ConfigParser()
#     config.read(CONFIGURATION_FILE)
#
# FILENAME =  config[SECTION_PATH]["FILENAME"]
# TMPDIR =    config[SECTION_PATH]["TMPDIR"]
# DATADIR =   config[SECTION_PATH]["DATADIR"]
# LOGDIR =    config[SECTION_PATH]["LOGDIR"]
# BACKUP =    config[SECTION_PATH]["BACKUP"]
# TEST_RESULT =   config[SECTION_PATH]["TEST_RESULT"]
#
#
# PAYLOAD_LIST =  config[SECTION_MQTT]["PAYLOAD_LIST"]
# QoS =           config[SECTION_MQTT]["QoS"]
# N_PACKET_SEND = config[SECTION_MQTT]["N_PACKET_SEND"]
# TOPIC =         config[SECTION_MQTT]["TOPIC"]
#
# TCPDUMP_FILTER = config[SECTION_SNIFFER]["TCPDUMP_FILTER"]
# IFC =       config[SECTION_SNIFFER]["IFC"]
#
# GW_IP =     config[SECTION_PING]["GW_IP"]
# conf_ready = True

