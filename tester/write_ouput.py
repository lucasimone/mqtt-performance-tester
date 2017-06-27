
from tester.analyze import computeTime


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


def write_test_result(index, payload, file_id,  num_test, path=DATA_PATH):

    filename = "/".join([".", path, TEST_RESULT])
    data = computeTime('%s.json' % file_id, num_test=num_test)

    with open(filename, "a") as fw:
        line = []
        line.append("\n")
        line.append("---MQTT TEST n.{0}\n".format(index))
        line.append("|- FILENAME: {}\n".format(file_id))
        line.append("|- PAYLOAD :{}\n".format(payload))
        line.append("|- ITERATION:{0}\n".format(num_test))
        line.append("|- PDrop:{0}\n".format(data.get_packet_drop(payload)))
        line.append("|- E2E:{0}\n".format(data.get_e2e()))
        line.append("|- TCP Overhead:{}\n".format(data.get_tcp_overhead()))
        line.append("|- PDR: {0}\n".format(data.get_pdr()))
        line.append("\n")
        fw.writelines(" ".join(line))
        fw.close()

    #get path






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