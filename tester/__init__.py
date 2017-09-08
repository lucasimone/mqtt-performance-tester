_last_capture = None



FILENAME = "data/mqtt_capture"


TMPDIR = "tmp"
DATADIR = "data"
LOGDIR = "log"
BACKUP = "backup"



TEST_RESULT= "data/report.txt"
#PAYLOAD_LIST = [128, 256, 512, 1024]
PAYLOAD_LIST = [1024]
QoS = [1]
N_PACKET_SEND = 10
TOPIC = 'topic'


IFC = ""
WAIT_START_TCPDUMP = 1
WAIT_CLOSE_TCPDUMP = 2
TCPDUMP_FILTER =  'tcp'