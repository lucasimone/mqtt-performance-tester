from mqtt_performance_tester.analyze_with_dup import computeTime, compute_e2e_latency


DATA_PATH   = "data"
TEST_RESULT = "report.txt"
GRAPH_RESULT = "e2e.dat"


def init_output_file(num_test, path = DATA_PATH):

    filename = "/".join([".", path, TEST_RESULT])
    with open(filename, "a") as fw:
        line = []
        line.append ( "COMPUTE PATH:%s with %d tests " %(path, num_test))
        line.append("\n\n")
        fw.writelines(" ".join(line))
        fw.close()


def write_test_result(index, payload, file_id,  num_test, qos, dir_path=DATA_PATH):

    filename = "/".join([".", dir_path, TEST_RESULT])
    data = computeTime('%s.json' % file_id,  qos=qos, num_test=num_test)
    min_e2e, max_e2e, avg_e2e, values = compute_e2e_latency(data.packets)
    overhead_tcp, overhead_mqtt = data.get_tcp_overhead()

    with open(filename, "a") as fw:
        line = []
        line.append("\n")
        line.append(" |-------------------------------------------------\n")
        line.append(" |-- MQTT TEST n.{0}\n".format(index))
        line.append(" |-------------------------------------------------\n")
        line.append(" |-- FILENAME: {}\n".format(file_id))
        line.append(" |-- PAYLOAD :{}\n".format(payload))
        line.append(" |-- QoS :{}\n".format(qos))
        line.append(" |-- ITERATION:{0}\n".format(num_test))
        line.append(" |------------------ Statistics ------------------\n")
        line.append(" |- Packet Drop:{0}% MQTT_PAYLOAD / TCP+MQTT_TCP\n".format(data.get_packet_drop()))
        line.append(" |-------------------------------------------------\n")
        line.append(" |- E2E Latency: Min: {0}\n".format(min_e2e))
        line.append(" |- E2E Latency: MAX: {0}\n".format(max_e2e))
        line.append(" |- E2E Latency: AVG: {0}\n".format(avg_e2e))
        line.append(" |-------------------------------------------------\n")
        line.append(" |- TCP Overhead:{}% [ TCP_ONLY / TCP+MQTT_TCP]\n".format(overhead_tcp))
        line.append(" |- TCP Overhead:{}% [ MQTT_PAYLOAD / FULL_TCP]\n".format(overhead_mqtt))
        line.append(" |-------------------------------------------------\n")
        line.append(" | Detected %d MQTT packets\n" % len(data.packets))
        line.append(" |-------------------------------------------------\n")
        for key in data.count_mqtt_type.keys():
            line.append(' |---- n. {1} of MQTT msg: {0}\n'.format(key, data.count_mqtt_type[key]))
        line.append(' |---------------------------------------\n')
        line.append(" |---- %d TOTAL MQTT msg exchanged \n" % (data.num_mqtt))
        line.append(' |---------------------------------------\n')
        line.append(" |--- TCP Message:         %s\n" % data.num_tcp)
        line.append(' |--- MQTT Message:        %d\n' % data.num_mqtt)
        line.append(' |--- UDP Message:         %d\n' % data.num_upd)
        line.append(' |--- OTHER Message:       %d\n' % data.num_others)
        line.append(' |---------------------------------------\n')
        line.append(' |--- TCP  packets size:   %d\n' % data.size_tcp)
        line.append(' |--- MQTT TCP size:       %d\n' % data.mqtt_tcp_size)
        line.append(' |--- TCP + TCP:MQTT size: %d\n' % (data.size_tcp + data.mqtt_tcp_size))
        line.append(' |--- MQTT payload size:   %d\n' % data.mqtt_payload_size)
        line.append(' |--- UPD packets size:    %d\n' % data.size_udp)
        line.append(' |--- OTHERS packets size: %d\n' % data.size_others)
        line.append(' |--- TCP+UDP+OTHER size:  %d\n' % (data.size_tcp + data.size_udp + data.size_others + data.mqtt_tcp_size))
        line.append(' |--- TOTAL Frames size:   %d\n' % data.frames_size)
        line.append(" |-------------------------------------------------\n")
        line.append("\n")
        fw.writelines(" ".join(line))
        fw.close()



def write_greph_file(index, res, timeout, rand_factor, retry, avg_time, pdr, e2e, p_success, path):
    """
    Create a file for plot the info
    :return:
    """
    filename = "/".join([".", path, GRAPH_RESULT])

    with open(filename, "a") as fw:
        line = []
        line.append("{0}".format(index))
        line.append("{0}".format(timeout))
        line.append("{0}".format(rand_factor))
        line.append("{0}".format(retry))
        line.append("{0}".format(""))
        line.append("{0}".format(avg_time))
        line.append("{0}".format(pdr))
        line.append("{0}".format(e2e))
        line.append("{0}".format(p_success))
        line.append("{0}".format(res))
        line.append("\n")
        fw.writelines("\t".join(line))
        fw.close()