#!/usr/bin/python
import click
import glob
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.animation as animation
from matplotlib.patches import Polygon

import matplotlib as mpl

## agg backend is used to create plot as a .png file
mpl.use('agg')



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



def plot_e2e(path):


    index = 111
    for f in glob.glob(os.path.join(path, '*.json')):
        info = f.split("_")
        num = int(info[8].replace(".json", ""))
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



def create_cvs(filename, values):

    with open('%s.csv' % filename, 'w') as csvfile:
        fieldnames = ['payload', 'values']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # writer.writeheader()
        for payload in values.keys():
            writer.writerow({'payload': payload, 'values': values[payload]})


def compute_all_file(path):


    sims  = dict()
    link_dis = ""
    for f in glob.glob(os.path.join(path, '*.json')):
        parts = f.split("/")
        file_id  = parts[2].replace(".json", "")
        link_dis = parts[1]
        info = file_id.split("_")
        num = int(info[8].replace(".json", ""))
        qos = info[3]
        payload = info[5]
        data = computeTime(f, num, qos)
        min_v, avg_v, max_v, all_data = compute_e2e_latency(data.packets)
        if qos not in sims:
            sims[qos] = dict()
        sims[qos][payload] = all_data

    for qos in sims:
        create_cvs("%s_qos_%s"%(link_dis, qos), sims[qos])



def clean_data(data):

    out = []
    for v in data.split():
        for c in ['[', ',', ']']:
            v = v.replace(c, "")
        out.append(float(v))

    return out



def plot_cvs_iteration(filename):


    payloads = dict()
    with open(filename) as csvfile:
        fieldnames = ['filename', 'values']
        reader = csv.DictReader(csvfile, fieldnames=fieldnames)
        for row in reader:
            payloads[row['filename']] = clean_data(row['values'])

    try:
        info = filename.split("_")
        num = int(info[1])
        qos = int(info[7].replace(".csv", ""))
        link_off = info[4]
    except:
        print ("Please provide info for the simulation %s" %filename)
        num = int(input("N. Iteration:"))
        qos = int(input("Qos:"))
        link_off = input("Link disruption:")



    for payload in payloads.keys():



        fig = plt.figure()
        ax = fig.add_subplot(111)

        plt.axis([0, 100, 0, 100])
        ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
        ax.xaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
        values = payloads[payload]

        x_pos = [x for x in range(len(values))]
        ax.plot(x_pos, values, 'k', x_pos, values, 'bo', lw=2)
        ax.set_xlabel( 'N. Iteration {}'.format(num))
        ax.set_ylabel('Latency (s).')
        ax.set_title("E2E Latency for QoS:%d - Payload:%s - Link off %s" % (qos, payload, link_off ))

        min_v = min(values)
        max_v = max(values)
        avg_v = sum(values)*0.1 / len(values)

        for x, y in zip(x_pos, values):
            if y in [min_v, max_v, avg_v] or y > (max_v-min_v)/2:
                ax.annotate('%.2f'%y, xy=(x, y), xytext=(x + 2, y), color='blue')


        fig.savefig('es_500_mqtt_qos_%d_payload_%s_linkoff_%s.png' % (qos, payload, link_off), bbox_inches='tight')



    keys =  sorted([int(i) for i in payloads.keys()])
    values = dict()
    medians = dict()
    for k in keys:
        all_num =  payloads[str(k)]
        avg =  sum(all_num)*0.1 / len(all_num)
        medians[k] = avg
        reduced = [x for x in all_num if x < 100]
        values[k] = reduced


    fig = plt.figure()
    plt.axis([0, 7, 0, 100])
    fig.canvas.set_window_title(filename)
    ax1 = fig.add_subplot(111)

    bp = plt.boxplot([values[x] for x in keys], 0, 'gD')
    #plt.setp(bp['boxes'], color='blue')
    #plt.setp(bp['whiskers'], color='green')
    for flier in bp['fliers']:
        flier.set(marker='o', color='#e7298a', alpha=0.5)


    # Add a horizontal grid to the plot, but make it very light in color
    # so we can use it for reading data values but not be distracting
    ax1.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.8)
    # Hide these grid behind plot objects
    ax1.set_axisbelow(True)
    ax1.set_title('MQTT QoS %d with %s of link disruption' %(qos, link_off))
    ax1.set_xlabel('Payloads')
    ax1.set_ylabel('Latency (s)')
    ax1.set_xticklabels(keys)

    for line in bp['medians']:
        # get position data for median line
        x, y = line.get_xydata()[1]  # top of median line
        # overlay median value
        plt.text(x, y, '%.2f' % y,
                 horizontalalignment='center')  # draw above, centered

    for line in bp['boxes']:
        x, y = line.get_xydata()[0]  # bottom of left line
        plt.text(x, y, '%.2f' % y,
                 horizontalalignment='center',  # centered
                 verticalalignment='top')  # below
        x, y = line.get_xydata()[3]  # bottom of right line
        plt.text(x, y, '%.2f' % y,
                 horizontalalignment='center',  # centered
                 verticalalignment='top')  # below



    ## Remove top axes and right axes ticks
    ax1.get_xaxis().tick_bottom()
    ax1.get_yaxis().tick_left()
    # Save the figure
    fig.savefig('es_mqtt_qos_%d_linkoff_%s.png'%(qos,link_off), bbox_inches='tight')


    #plt.show()


if __name__ == '__main__':

    #directory = "all_sim/data_500_mqtt_with_10%_off"
    ## CREATE CSV FILES

    #compute_all_file("all_sim/data_500_mqtt_with_10%_off")
    #compute_all_file("all_sim/data_500_mqtt_with_30%_off")
    #compute_all_file("all_sim/data_500_mqtt_with_50%_off")
    #compute_all_file("all_sim/data_500_mqtt_with_70%_off")

    # plot_e2e(directory)
    # create_cvs(directory)


    path  = input("DIR:")

    for filename in glob.glob(os.path.join(path, '*.csv')):
        print("%s" %(filename))
        plot_cvs_iteration("%s" %filename)

    #plot_cvs_iteration('ld30_qos_1.csv')
    # plot_cvs_iteration('plots/data_500_mqtt_with_70%_off_qos_1.csv')
    #
    #
    # plot_cvs_iteration('plots/data_500_mqtt_with_10%_off_qos_1.csv')
    # plot_cvs_iteration('plots/data_500_mqtt_with_10%_off_qos_2.csv')
    #
    #
    # plot_cvs_iteration('plots/data_500_mqtt_with_30%_off_qos_1.csv')
    # plot_cvs_iteration('plots/data_500_mqtt_with_30%_off_qos_2.csv')
    #
    # plot_cvs_iteration('plots/data_500_mqtt_with_50%_off_qos_1.csv')
    # plot_cvs_iteration('plots/data_500_mqtt_with_50%_off_qos_2.csv')