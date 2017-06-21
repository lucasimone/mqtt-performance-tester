import errno
from tester import *
from tester.commands import *
from tester.analyze import N_PACKET_SEND
from tester.write_ouput import write_test_result


def start_mqtt_client(qos, payload):
    global logger

    msg = "Start MQTT CLIENT QoS=%d Payload:%d"  %(qos, payload)
    logger.debug(msg)

    params = 'echo %s' %msg
    os.system(params)



if __name__ == '__main__':


    # generate dirs
    for d in TMPDIR, DATADIR, LOGDIR:
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    logger.debug("START TEST...")
    index = 0
    for qos in (1, 2):
        for payload in (128, 256, 1024):

                file_id = ('_'.join([FILENAME,
                                    "qos",
                                    str(qos),
                                    "payload",
                                    str(payload)
                                    ]))

                file_name = '%s.pcap' % file_id
                launch_sniffer(file_name, IFC, other_filter='tcp and port 1883')
                start_mqtt_client(qos=qos, payload=payload)
                stop_sniffer()
                decode_pcap(file_name)
                write_test_result(index, payload, file_id, N_PACKET_SEND)

                index+=1

    logger.debug("TEST is over!")