import errno

from tester import *
from tester.commands import *
from tester import N_PACKET_SEND, PAYLOAD_LIST, TOPIC
from tester.write_ouput import write_test_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start_mqtt_client(set_qos, payload_size):

    payload = "[START PAYLOAD - SIZE BYTE {0}]".format(payload_size)
    stop    = "[END PAYLOAD]"
    num_char = payload_size - len(payload) - len (stop)
    for i in range(num_char):
        payload += "X"
    payload+=stop


    #logger.debug("Payload size: %d" % len(payload))

    params = "mosquitto_pub -q %d -t %s -m '%s'" % (set_qos, TOPIC, payload)

    #logger.debug(params)
    for count in range( N_PACKET_SEND):
        print(" >>> Sending packt n. %d/%s  \t Payload: %s" %(count+1, N_PACKET_SEND, payload_size))
        os.system(params)


def backup_data_folder():
    if os.path.exists(DATADIR):
        old_data = '_'.join([DATADIR, str(time.time())])
        os.rename(DATADIR, old_data)

    # generate dirs
    for d in TMPDIR, DATADIR, LOGDIR, BACKUP:
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    if old_data:
        os.rename(old_data, "%s/%s" % (BACKUP, old_data))

if __name__ == '__main__':


    backup_data_folder()


    logger.debug("START  MQTT TEST...")
    index = 0
    for qos in QoS:
        for payload in PAYLOAD_LIST:

                file_id = ('_'.join([FILENAME,
                                    "qos",
                                    str(qos),
                                    "payload",
                                    str(payload)
                                    ]))

                file_name = '%s.pcap' % file_id
                launch_sniffer(file_name, IFC, other_filter=TCPDUMP_FILTER)
                time.sleep(WAIT_START_TCPDUMP)
                start_mqtt_client(qos, payload)
                print(" >>> SENT ALL PACKETS <<<<")

                check_end_of_transmission(file_name, qos, N_PACKET_SEND)
                logger.debug("KILL TCPDUMP...")
                stop_sniffer()

                decode_pcap(file_name)
                write_test_result(index, payload, file_id, N_PACKET_SEND, qos)

                index+=1


    logger.debug("TEST MQTT completed!")
