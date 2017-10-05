#!/usr/bin/python
import matplotlib.pyplot as plt
import numpy as np
from mqtt_performance_tester.analyze_with_dup import computeTime, compute_e2e_latency



def plot_e2e_for_one_file(filename):


    file_id=filename.split("/")
    file_info=file_id[len(file_id)-1].replace(".json","").split("_")


    data = computeTime(filename, 500, 1)
    min_v, max_v, avg_v, values = compute_e2e_latency(data.packets)

    x = [v for v in range(len(values))]
    y = [v for v in values]

    fig = plt.figure()

    ax1 = fig.add_subplot(111)

    ax1.set_title("E2E Latecency for QoS:%s - Payload:%s" % (file_info[2],file_info[4]))
    ax1.set_xlabel('N. Iteration')
    ax1.set_ylabel('Latency (s).')

    ax1.plot(x, y, c='r', label='E2E Latency(s)')
    plt.show()


def plot_e2e():
    np.random.seed(123)
    all_data = [np.random.normal(0, std, 100) for std in range(1, 6)]

    fig, axes = plt.subplots()

    # rectangular box plot
    bplot1 = axes.boxplot(all_data,
                             vert=True,  # vertical box aligmnent
                             patch_artist=True)  # fill with color

    # fill with colors
    colors = ['pink', 'lightblue', 'lightgreen', 'yellow', 'green']
    for patch, color in zip(bplot1['boxes'], colors):
            patch.set_facecolor(color)

    # adding horizontal grid lines
    axes.yaxis.grid(True)
    axes.set_xticks([y + 1 for y in range(len(all_data))], )
    axes.set_xlabel('xlabel')
    axes.set_ylabel('ylabel')

    # add x-tick labels
    plt.setp(axes, xticks=[y + 1 for y in range(len(all_data))],
             xticklabels=['128', '256', '512', '1024', '1152', '1280'])

    plt.show()





def plot_overhead(filename):
    # line.append(' |--- TCP  packets size:   %d\n' % data.size_tcp)
    # line.append(' |--- MQTT TCP size:       %d\n' % data.mqtt_tcp_size)
    # line.append(' |--- TCP + TCP:MQTT size: %d\n' % (data.size_tcp + data.mqtt_tcp_size))
    # line.append(' |--- MQTT payload size:   %d\n' % data.mqtt_payload_size)
    # line.append(' |--- UPD packets size:    %d\n' % data.size_udp)
    # line.append(' |--- OTHERS packets size: %d\n' % data.size_others)
    # line.append(
    #     ' |--- TCP+UDP+OTHER size:  %d\n' % (data.size_tcp + data.size_udp + data.size_others + data.mqtt_tcp_size))
    # line.append(' |--- TOTAL Frames size:   %d\n' % data.frames_size)

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
    json_file = "backup/data_1507099161.54/mqtt_qos_1_payload_1280_num_req_500.json"
    #plot_e2e_for_one_file(json_file)
    #plot_overhead(json_file)
    plot_e2e()