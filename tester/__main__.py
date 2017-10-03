import errno
import shutil

from tester import *
from tester.commands import *
from tester import N_PACKET_SEND, PAYLOAD_LIST, TOPIC
from tester.write_ouput import write_test_result

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def create_paylod(size, num, qos):
    payload = "[START PAYLOAD - N.{1} SIZE BYTE {0} QOS={2}]".format(size, num+1, qos)
    stop = "[END PAYLOAD N.{0}]".format(num+1)
    num_char = size - len(payload) - len(stop)
    for i in range(num_char):
        payload += "X"
    payload += stop
    return payload

def start_mqtt_client(set_qos, payload_size):

    for count in range( N_PACKET_SEND):

        params = "mosquitto_pub -d -h %s -q %d -t %s -m '%s'" % (GW_IP, set_qos, "%s-%d"%(TOPIC,set_qos), create_paylod(payload_size, count, set_qos))
        print(" >>> Sending packet n.%d/%s \tPayload: %s" %(count+1, N_PACKET_SEND, payload_size))
        os.system(params)


def backup_data_folder():

    if os.path.exists(DATADIR):
        old_data = '_'.join([DATADIR, str(time.time())])
        os.rename(DATADIR, old_data)
        shutil.move(old_data, BACKUP)

    # generate dirs
    for d in TMPDIR, DATADIR, LOGDIR, BACKUP:
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise


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
                                    str(payload),
                                    "num_req",
                                    str( N_PACKET_SEND)
                                    ]))

                file_name = '%s.pcap' % file_id
                launch_sniffer(file_name, IFC, other_filter=TCPDUMP_FILTER)
                time.sleep(2)
                start_mqtt_client(qos, payload)
                print(" >>> SENT ALL PACKETS <<<<")

                #check_end_of_transmission(file_name, qos, N_PACKET_SEND)
                #logger.debug("KILL TCPDUMP...")
                stop_sniffer()

                decode_pcap(file_name)
                #write_test_result(index, payload, file_id, N_PACKET_SEND, qos)

                index+=1


    logger.debug("TEST MQTT completed!")
