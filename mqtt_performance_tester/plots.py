#!/usr/bin/python
import click
import glob
import os

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.animation as animation


from mqtt_performance_tester.analyze_with_dup import computeTime, compute_e2e_latency

@click.command()
@click.option('--path', prompt='Path of the simulation', help='')
def gen_plot(path):
    print(path)


def plot_e2e_for_one_file(filename):


    file_id=filename.split("/")
    file_info=file_id[len(file_id)-1].replace(".json","").split("_")


    data = computeTime(filename, 500, 1)
    min_v,  avg_v, max_v, values = compute_e2e_latency(data.packets)

    x = [v for v in range(len(values))]
    y = [v for v in values]

    fig = plt.figure()

    ax1 = fig.add_subplot(111)

    ax1.set_title("E2E Latecency for QoS:%s - Payload:%s" % (file_info[2],file_info[4]))
    ax1.set_xlabel('N. Iteration')
    ax1.set_ylabel('Latency (s).')
    ax1.set_xticks(ax1.get_xticks()[::2])
    plt.axis([0, 501, 0, max(values)+10])
    ax1.plot(x, y, 'k', x, y, 'bo', label='E2E Latency(s)')
    plt.show()


def plot_latency(filename):

    plt.rcdefaults()
    fig, ax = plt.subplots()

    data = computeTime(filename, 500, 1)
    min_v, avg_v, max_v, all_data = compute_e2e_latency(data.packets)

    x_pos = [x for x in range(len(all_data))]

    ax.plot(x_pos, all_data, 'k', x_pos, all_data, 'bo',  lw=2)
    ax.set_xlabel('N. Publish Message')
    ax.set_title('Latency (s) - Min{0}, Max{1}, Avg:{2}'.format(round(min_v,2), round(max_v,2), round(avg_v,2)))

    previous = 0
    for x, y in zip(x_pos, all_data):
        if y in [min_v, max_v, avg_v] or y >= (max_v+min_v)/2:
            ax.annotate(str(round(y, 2)), xy=(x, y), xytext=(x+5, y), color='blue')
        previous = y

    plt.show()


def plot_e2e(path):


    index = 212
    for f in glob.glob(os.path.join(path, '*.json')):
        info = f.split("_")
        num = int(info[8].replace(".json",""))
        qos = info[3]
        data = computeTime(f, num, qos)
        min_v, avg_v, max_v, all_data = compute_e2e_latency(data.packets)

        fig = plt.figure()

        ax = fig.add_subplot(index)

        x_pos = [x for x in range(len(all_data))]

        ax.plot(x_pos, all_data, 'k', x_pos, all_data, 'bo', lw=2)
        ax.set_xlabel('N. Iteration - E2E Min{0}, Max{1}, Avg:{2}'.format(round(min_v, 2), round(max_v, 2), round(avg_v, 2)))
        ax.set_ylabel('Latency (s).')
        ax.set_title("E2E Latency for QoS:%s - Payload:%s" % (qos, info[4]))


        for x, y in zip(x_pos, all_data):
            if y in [min_v, max_v, avg_v] or y >= (max_v + min_v) / 2:
                ax.annotate(str(round(y, 2)), xy=(x, y), xytext=(x + 2, y), color='blue')


    plt.show()






def plot_overhead(filename):

    file_id = filename.split("/")
    file_info = file_id[len(file_id) - 1].replace(".json", "").split("_")

    data = computeTime(filename, file_info[7], file_info[2])
    plt.rcdefaults()
    fig, ax = plt.subplots()
    tags = ('TCP', 'MQTT', 'UPD', 'OTHERS', 'Frame')
    values = (data.size_tcp, data.mqtt_tcp_size, data.size_udp, data.size_others, data.frames_size)

    y_pos = np.arange(len(tags))
    error = np.random.rand(len(tags))



    ax.barh(y_pos, values, xerr=error, align='center', color='blue', ecolor='black')
    ax.set_yticks(y_pos)
    ax.set_yticklabels(tags)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Protocol Size')
    ax.set_title('Transmission overhead')


    plt.show()

if __name__ == '__main__':
    json_file = "backup/data_1507099161.54/mqtt_qos_1_payload_128_num_req_500.json"
    plot_e2e("backup/data_1507187908.46")