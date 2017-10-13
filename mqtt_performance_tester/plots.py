#!/usr/bin/python
import click
import glob
import os
from collections import OrderedDict

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
        ax.set_title("E2E Latency for QoS:%s - Payload:%s" % (qos, info[5]))


        for x, y in zip(x_pos, all_data):
            if y in [min_v, max_v, avg_v] or y >= (max_v + min_v) / 2:
                ax.annotate(str(round(y, 2)), xy=(x, y), xytext=(x + 2, y), color='blue')


    plt.show()


def plot_e2e_box(path):

    res = ['128', '256', '512', '1024', '1152', '1280', '1408']
    #info = f.split("_")
    #num = int(info[8].replace(".json",""))
    #qos = info[3]

    #data = computeTime(f, num, qos)
    #min_v, avg_v, max_v, all_data = compute_e2e_latency(data.packets)

    fig = plt.figure()

    ax = fig.add_subplot(111)
    ax.set_title('Latency (50% link disruption)')
    ax.yaxis.grid(True)
    ax.set_xticks([y + 1 for y in range(len(res))])
    ax.set_xlabel('Four separate samples')
    ax.set_ylabel('Observed values')

    # add x-tick labels
    plt.setp(ax, xticks=[y + 1 for y in range(len(res))],
                 xticklabels=res)


    plt.show()


def test():
    # Unlike with bar plots, there is no need to aggregate the data
    # before plotting
    # However the data for each group (day) needs to be defined

    res = []
    latency_q1 = [[],[],[],[],[],[]]
    latency_q2 = [[],[],[],[],[],[]]

    res = ['128','256', '512', '1024', '1152', '1280']


    for f in glob.glob(os.path.join('backup/data', '*.json')):
        info = f.split("_")
        num = int(info[8].replace(".json", ""))
        qos = info[3]
        payload = info[5]
        data = computeTime(f, num, qos)
        min_v, avg_v, max_v, values = compute_e2e_latency(data.packets)
        res.append(payload)
        if qos == '1':
            latency_q1[res.index(payload)]=values
        else:
            latency_q2[res.index(payload)]=values

    # Define a function to create a boxplot:
    def boxplot(x_data, y_data, base_color, median_color, x_label, y_label, title):
        # _, ax = plt.subplots()
        #
        # # Draw boxplots, specifying desired style
        # ax.boxplot(y_data
        #            # patch_artist must be True to control box fill
        #            , patch_artist=True
        #            # Properties of median line
        #            , medianprops={'color': median_color}
        #            # Properties of box
        #            , boxprops={'color': base_color, 'facecolor': base_color}
        #            # Properties of whiskers
        #            , whiskerprops={'color': base_color}
        #            # Properties of whisker caps
        #            , capprops={'color': base_color})
        #
        # # By default, the tick label starts at 1 and increments by 1 for
        # # each box drawn. This sets the labels to the ones we want
        # ax.set_xticklabels(x_data)
        # ax.set_ylabel(y_label)
        # ax.set_xlabel(x_label)
        # ax.set_title(title)


        fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))
        # Draw boxplots, specifying desired style
        ax[0].boxplot(y_data[0]
                   # patch_artist must be True to control box fill
                   , patch_artist=True
                   # Properties of median line
                   , medianprops={'color': median_color}
                   # Properties of box
                   , boxprops={'color': base_color, 'facecolor': base_color}
                   # Properties of whiskers
                   , whiskerprops={'color': base_color}
                   # Properties of whisker caps
                   , capprops={'color': base_color})

        # By default, the tick label starts at 1 and increments by 1 for
        # each box drawn. This sets the labels to the ones we want
        ax[0].set_xticklabels(x_data)
        ax[0].set_ylabel(y_label)
        ax[0].set_xlabel(x_label)
        ax[0].set_title("QoS 1")

        ax[1].boxplot(y_data[1]
                      # patch_artist must be True to control box fill
                      , patch_artist=True
                      # Properties of median line
                      , medianprops={'color': median_color}
                      # Properties of box
                      , boxprops={'color': base_color, 'facecolor': base_color}
                      # Properties of whiskers
                      , whiskerprops={'color': base_color}
                      # Properties of whisker caps
                      , capprops={'color': base_color})

        # By default, the tick label starts at 1 and increments by 1 for
        # each box drawn. This sets the labels to the ones we want
        ax[1].set_xticklabels(x_data)
        ax[1].set_ylabel(y_label)
        ax[1].set_xlabel(x_label)
        ax[1].set_title("QoS 2")

        # # Draw boxplots, specifying desired style
        # ax.boxplot(y_data
        #            # patch_artist must be True to control box fill
        #            , patch_artist=True
        #            # Properties of median line
        #            , medianprops={'color': median_color}
        #            # Properties of box
        #            , boxprops={'color': base_color, 'facecolor': base_color}
        #            # Properties of whiskers
        #            , whiskerprops={'color': base_color}
        #            # Properties of whisker caps
        #            , capprops={'color': base_color})
        #
        # # By default, the tick label starts at 1 and increments by 1 for
        # # each box drawn. This sets the labels to the ones we want
        # ax.set_xticklabels(x_data)
        # ax.set_ylabel(y_label)
        # ax.set_xlabel(x_label)
        # ax.set_title(title)

    # Call the function to create plot
    boxplot(  x_data=res
            , y_data=[latency_q1, latency_q2]
            , base_color='#539caf'
            , median_color='#297083'
            , x_label='Payload Size'
            , y_label='Latency (ms)'
            , title='QoS 1')

    plt.show()

def plot_single_file(filename):

    info = filename.split("_")
    num = int(info[8].replace(".json",""))
    qos = info[3]
    data = computeTime(filename, num, qos)
    min_v, avg_v, max_v, all_data = compute_e2e_latency(data.packets)

    fig = plt.figure()

    ax = fig.add_subplot(111)
    x_pos = [x for x in range(len(all_data))]
    ax.plot(x_pos, all_data, 'k', x_pos, all_data, 'bo', lw=2)
    ax.set_xlabel('N. Iteration - E2E Min{0}, Max{1}, Avg:{2}'.format(round(min_v, 2), round(max_v, 2), round(avg_v, 2)))
    ax.set_ylabel('Latency (s).')
    ax.set_title("E2E Latency for QoS:%s - Payload:%s" % (qos, info[5]))

    for x, y in zip(x_pos, all_data):
        if y in [min_v, max_v, avg_v] or y >= (max_v + min_v) / 2:
            ax.annotate(str(round(y, 2)), xy=(x, y), xytext=(x + 2, y), color='blue')
    plt.show()






def plot_tcp_overhead(filename):


    file_info = filename.split("/")[2].replace(".json", "").split("_")
    num = file_info [8]
    qos = file_info [3]
    payload = file_info [5]


    data = computeTime(filename, num, qos)
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
    json_file = "backup/data/mqtt_capture_qos_1_payload_256_num_req_500.json"
    plot_e2e("backup/data")
    #plot_e2e_box(json_file)
    #test()