import logging
import os
import json

# # init logging to stnd output and log files
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
#
# # default handler
# sh = logging.StreamHandler()
# sh.setLevel(logging.DEBUG)
# sh.setFormatter(logging.Formatter('%(asctime)s  %(filename)-20s:%(lineno)-5d %(levelname)-8s %(message)s'))
# logger.addHandler(sh)
#


with open("test1.json") as file:
    json_data = json.load(file)
    file.close()

print(json_data[0]['_type'])