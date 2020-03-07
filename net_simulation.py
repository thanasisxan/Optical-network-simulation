import random
from collections import deque

# Πιθανότητες άφιξης και μετάδοσης
arriving_prob = 1
transmitting_prob = 0.5

timeslots = 1000
stations = 8



totalpacketscreated = 0
totalpacketssent = 0
totalpacketslost = 0
# μέγιστος αριθμός πακέτων προς μετάδοση
max_packet_transmitted = stations * timeslots

# συνολική καθυστέρηση
totaldelay = 0


class Station:
    def __init__(self, name, wavelength_int):
        self.name = name
        self.wavelength_int = wavelength_int
        self.packet_buffer_fifo = deque([])
        self.trx_current_station = 0
        self.current_ts = 0
        # πίνακας που αποθηκεύει το timeslot άφιξης του κάθε πακέτου, index ο αριθμός του πακέτου που αναφερόμαστε
        self.p_ts_added = [None] * max_packet_transmitted

    def net_queue_ts_start(self, current_ts):
        global totalpacketscreated, totalpacketslost
        prob_arrive = random.random()
        prob_transmit = random.random()
        self.trx_current_station = 0
        self.current_ts = current_ts

        print(self.name)

        if prob_arrive <= arriving_prob:
            # υπάρχει καινούργιο πακετο για να προστεθεί στην ουρά (arrival)
            totalpacketscreated += 1
            if len(self.packet_buffer_fifo) < 5:
                self.packet_buffer_fifo.appendleft(totalpacketscreated)
                self.p_ts_added.insert(totalpacketscreated, self.current_ts)
                print('packet', totalpacketscreated, 'successfully added in queue of station', self.name, '!')
            else:
                print('packet not added in queue (queue full)')
                totalpacketscreated -= 1
                totalpacketslost += 1
        else:
            print('there are no new arrived packets')

        if prob_transmit <= transmitting_prob:
            if len(self.packet_buffer_fifo) >= 1:
                # θα γίνει απόπειρα μετάδοσης ενός πακέτου
                self.trx_current_station = 1
            else:
                # δεν υπάρχουν πακέτα για μετάδοση
                self.trx_current_station = 0
                # print('there are no packets to be transmitted')
        else:
            self.trx_current_station = 0

        print('Packets queue contents:', list(self.packet_buffer_fifo))
        return self.trx_current_station

    def net_queue_ts_finish_trx_no_collision(self, current_ts):
        # επιτυχής μετάδοση
        global totaldelay, totalpacketssent
        packet_no = self.packet_buffer_fifo.pop()
        packet_delay = current_ts - self.p_ts_added[packet_no]
        print('\npacket', packet_no, 'successfully transmitted!'
                                     ' with delay:', packet_delay, 'timeslots\n\n')
        totaldelay += packet_delay
        totalpacketssent += 1


def simulation_samewavelenth_stations(station_1, station_2, current_ts):
    trx_1 = station_1.net_queue_ts_start(current_ts)
    print('')
    trx_2 = station_2.net_queue_ts_start(current_ts)
    # Έλεγχος για collision μετάδοση σε άλλη περίπτωση
    if trx_1 == 1 and trx_2 == 1:
        # περίπτωση collision - τα πακετο προς μεταδοση δεν θα αφαιρεθεί από την ουρά
        # και θα μεταδοθουν σε επομενο timeslot
        print('\nCollision!\n\n')
    elif trx_1 == 0 and trx_2 == 0:
        # περίπτωση όπου κανένας δεν μεταδίδει
        print('\nNo transmission\n\n')
    elif trx_1 == 1 and trx_2 == 0:
        # περίπτωση όπου θέλει να μεταδώσει μόνο ο ένας σταθμός
        station_1.net_queue_ts_finish_trx_no_collision(current_ts)
    elif trx_1 == 0 and trx_2 == 1:
        # περίπτωση όπου θέλει να μεταδώσει μόνο ο ένας σταθμός
        station_2.net_queue_ts_finish_trx_no_collision(current_ts)


station_l1_1 = Station('(Station 1) (λ1)', 1)
station_l1_2 = Station('(Station 2) (λ1)', 1)

station_l2_1 = Station('(Station 3) (λ2)', 2)
station_l2_2 = Station('(Station 4) (λ2)', 2)

station_l3_1 = Station('(Station 5) (λ3)', 3)
station_l3_2 = Station('(Station 6) (λ3)', 3)

station_l4_1 = Station('(Station 7) (λ4)', 4)
station_l4_2 = Station('(Station 8) (λ4)', 4)

# Προσομοίωση για T timeslots
# υποτίθεται οτι κάθε κάλεσμα της συνάρτησης simulation_samewavelenth_stations εκτελείται παράλληλα
# σε κάθε ξεχωριστό timeslot
for ts in range(timeslots):
    print('\n\n---===Timeslot:', ts, '===---\n')
    simulation_samewavelenth_stations(station_l1_1, station_l1_2, ts)
    simulation_samewavelenth_stations(station_l2_1, station_l2_2, ts)
    simulation_samewavelenth_stations(station_l3_1, station_l3_2, ts)
    simulation_samewavelenth_stations(station_l4_1, station_l4_2, ts)

print('\n\nTotal packets created:', totalpacketscreated)
print('Total packets sent:', totalpacketssent)
print('Total delay:', totaldelay)

# Υπολογισμός ζητουμένων
average_delay = totaldelay / totalpacketssent
throughput = totalpacketssent / timeslots
packet_loss_rate = totalpacketslost / totalpacketscreated

print('\nAverage delay:', average_delay)
print('Throughput:', throughput)
print('Packet loss rate:', packet_loss_rate)
