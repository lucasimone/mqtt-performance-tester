import click
import glob
import os
import datetime
import logging.handlers
from mqtt_performance_tester.commands import decode_pcap
from mqtt_performance_tester.write_ouput import *

LOG_FORMAT   = '%(levelname)-7s | %(asctime)s | %(name)40s:%(lineno)-3d| %(message)s'
LOG_FILENAME = "log/gen_report.log"


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(LOG_FORMAT)

sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.propagate = True

fh = logging.handlers.RotatingFileHandler(LOG_FILENAME, mode='a', maxBytes=2000, backupCount=0, encoding=None, delay=0)
fh.setFormatter(formatter)
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

logger.warning(" =====> New GenReport session started NOW !!!!")

@click.command()
@click.option('--path', prompt='PCAP(s) Path [ Default=backup]', help='The directory to check all data logs')
def analyze_in_path(path):

    if path == "":
        path = "backup"

    if not os.path.exists(path):
        logger.error("This directory does nor exists!")
        exit(-1)

    logger.info("Start iterating inside %s" %path)
    for directory in glob.glob('%s/*/' % path):
        logger.info("- Check directoty %s ..." % directory)
        report_file = "%s/report.txt" % directory
        if os.path.exists(report_file):
            logger.info("Backup old report")
            dt = str(datetime.datetime.now())
            rename_report = '%s/backup_report_' % (directory) + dt + '.txt'
            os.rename(report_file, rename_report)

        generate_report("%s" % (directory))


def generate_report(data_path):


    path = "%s/" % data_path
    index = 0
    logger.info("[-] Inspect Files in : %s" % path)
    #init_output_file(data_path, num_test)  # INIT FILE

    for filename in glob.glob(os.path.join(path, '*.pcap')):

        logger.info("[-] Read File : %s" % filename)

        try:

            file_id = filename.replace(".pcap", "")

            if not os.path.exists("%s.json"%file_id):
                decode_pcap(filename)

            logger.info("[-] |--- FileID : {}".format(file_id))
            file_info = file_id.split("_")
            qos = file_info[3]
            payload = file_info[5]
            iteration = file_info[8]

            logger.info("[-] |--- QoS: {}".format(qos))
            logger.info("[-] |--- Payload: {}".format(payload))
            logger.info("[-] |--- Iteration: {}".format(iteration))

            # write line for this filename
            write_test_result(index, payload, file_id,  iteration, qos, dir_path=path)
            index += 1
        except Exception as error:
            logger.error(" THIS DATA WAS GENERATED BY OLD CLIENT - SKIP!", error)




if __name__ == '__main__':


    logger.info("GET PATH")
    analyze_in_path()



