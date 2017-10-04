from mqtt_performance_tester import *
from mqtt_performance_tester.commands import *


if __name__ == '__main__':

    backup_data_folder()

    logger.info("Start MQTT Performance TEST - ")

    Config = read_configuration()
    QoS = [int(x) for x in Config.get("MQTT", "QoS").split(",")]

    IFC = Config.get("SNIFFER", "IFC")
    TCPDUMP_FILTER  = Config.get("SNIFFER", "TCPDUMP_FILTER")
    PAYLOAD_LIST    = [int(x) for x in Config.get("MQTT", "PAYLOAD_LIST").split(",")]
    N_PACKET_SEND   = Config.getint("MQTT", "N_PACKET_SEND")

    N_PACKET_SEND = Config.getint("MQTT", "N_PACKET_SEND")
    GW_IP = Config.get("PING", "GW_IP")
    TOPIC = Config.get("MQTT", "TOPIC")

    logger.debug("QoS: {}".format(Config.get("MQTT", "QoS")))
    logger.debug("PAYLOADs: {}".format(PAYLOAD_LIST))
    logger.debug("Iteration: {}".format(N_PACKET_SEND))


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
                start_mqtt_client(qos, payload, N_PACKET_SEND, TOPIC, GW_IP)
                logger.info(" >>> SENT ALL PACKETS <<<<")

                #check_end_of_transmission(file_name, qos, N_PACKET_SEND)
                #logger.debug("KILL TCPDUMP...")
                stop_sniffer()

                decode_pcap(file_name)
                #write_test_result(index, payload, file_id, N_PACKET_SEND, qos)

                index+=1


    logger.debug("Performance Test completed!")
