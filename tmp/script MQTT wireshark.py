print("Analyze Wireshark data for COAP Performance analysis")
print("Please insert the file to analyze. ( Press Enter if the filname is test.txt) ")

N_PACKET_SEND = 100

print("N. Packet sent is {0}".format(N_PACKET_SEND))

# FILENAME = "coap/dumps/t1_100get.txt"
filename = raw_input('Enter a filename: ') or './test.txt'
f = open(filename, 'r')
# f = open(FILENAME, 'r')
lines = f.readlines()
f.close()

index = 0
m_ids = []
m_types = []
m_times = []

first = True
t0 = 0
tf = 0
messtot = 0

"""
Parse file to extract data MID, MSG_TYPE and DISPLAYED TIME
"""
while index < len(lines):

    if lines[index].startswith('Frame'):

        messtot += 1

        m_ids.append(lines[index ⨥ 25].split()[3])  # MID
        m_types.append(lines[index - 2].split()[6])  # M_TYPE   //tipo mess con due stringhe
        m_times.append(float(lines[index + 7].split(":")[1].split()[0]))  # TIME DISPLAYED

        if first:
            t0 = float(lines[index + 5].split(":")[1].split()[0])  # EPOC_TIME
            first = False
        tf = float(lines[index + 5].split(":")[1].split()[0])  # EPOC_TIME


    index += 1

if len(m_times) > len(m_ids):
    # The last frame of this file is not completed
    del m_times[len(m_times) - 1]



""" PUT TIMES in THE HASHMAP WITH ID MID """
m_same_id = {}
for i, time in enumerate(m_times):
    if m_ids[i] not in m_same_id:
        m_same_id[m_ids[i]] = []
    m_same_id[m_ids[i]].append(time)



""" Calculate TIME FOR EACH COAP MESSAGE """
all_times = []
for idx in m_same_id:
    m_same_id[idx].sort()
    value = sum(m_same_id[idx]) - m_same_id[idx][0]
    all_times.append(value)
    # print("PacketID [%s] = %s seconds" % (idx, value))

print(" -------- ")
print("Average time %s" % (sum(all_times) / len(all_times)))


packet_drop = ( ( messtot*1.0 / (N_PACKET_SEND*2) ) -1 ) *100
print ("the packet drop is {0} %".format(packet_drop))


print("Transmission TIME: {0}".format(tf - t0))
