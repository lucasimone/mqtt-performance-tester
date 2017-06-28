import errno

from tester import *
from tester.commands import *
from tester import N_PACKET_SEND, PAYLOAD_LIST, TOPIC
from tester.write_ouput import write_test_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def start_mqtt_client(set_qos, payload_size):

    payload = ""
    for i in range(payload_size):
        payload += "X"

    #logger.debug("Payload size: %d" % len(payload))

    params = "mosquitto_pub -q %s -t %s -m %s -h localhost" % (set_qos, TOPIC, payload)

    #logger.debug(params)
    for count in range( N_PACKET_SEND):
        print(" >>> Sending packt n. %d/%s  \t Payload: %s" %(count+1, N_PACKET_SEND, payload_size))
        os.system(params)



if __name__ == '__main__':

    # generate dirs
    for d in TMPDIR, DATADIR, LOGDIR:
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

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
                launch_sniffer(file_name, IFC, other_filter='')
                time.sleep(1)
                start_mqtt_client(qos, payload)
                print(" >>> SENT ALL PACKETS <<<<")
                time.sleep(3)
                logger.debug("KILL TCPDUMP...")
                stop_sniffer()
                #show_pcap(file_name)
                decode_pcap(file_name)
                write_test_result(index, payload, file_id, N_PACKET_SEND)

                index+=1


    logger.debug("TEST MQTT is over!")
