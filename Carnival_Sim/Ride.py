from Customer import Customer
import queue
import numpy

class Ride:
    def __init__(self, cost, capacity, set_up_time, ride_time, leave_time, coaster):
        self.__cost = cost
        self.__capacity = capacity
        self.__set_up_time = set_up_time
        self.__ride_time = ride_time
        self.__leave_time = leave_time
        self.__current_active_time = 0
        self.__active = False
        self.__leaving = False
        self.__setting_up = True
        self.__wait_queue = queue.Queue(500)
        self.__is_coaster = coaster
        self.__line_length = 0
        self.__on_ride_list = queue.Queue(60)
        self.__on_ride_length = 0
        self.__start_to_finish = 0
        self.__times_ran = 0
        self.__worker_waiting = 0

#  -----------------------------------Getters and Setters---------------------------------------------

    def get_wait_queue(self):
        return self.__wait_queue

    def get_worker_idle_time(self):
        return self.__worker_waiting

    def get_on_ride_queue(self):
        return self.__on_ride_list

    def get_cost(self):
        return self.__cost

    def get_capacity(self):
        return self.__capacity

    def get_ride_time(self):
        return self.__ride_time

    def get_current_time(self):
        return self.__current_active_time

    def restart_time(self):
        self.__current_active_time = 0

    def increment_time(self):
        self.__current_active_time += 1

    def set_active(self, active):
        self.__active = active

    def is_active(self):
        return self.__active

    def add_rider(self, rider):
        self.__line_length += 1
        self.__wait_queue.put(rider)

    def get_line_length(self):
        return self.__line_length

    def get_start_to_finish_avg(self):
        return int(self.__start_to_finish/self.__times_ran)

#  ----------------------------------------------------------------------------------------------------------

    def update(self):
        move_list = queue.Queue(500)
        # If the line is empty,they are in the setting up, and it just started
        rand_set = numpy.random.normal(60, 10)  # this is the worker time
        rand_leave = numpy.random.normal(30, 5)
        if self.__line_length == 0 and self.__setting_up and self.__current_active_time == 0:
            self.__worker_waiting += 1
            return move_list
        #if the ride is the coaster
        if self.__is_coaster:
            #if the ride is setting up riders and there is still room, it will add the customers to the ride
            if self.__setting_up and self.__on_ride_length == 0:
                for x in range(0, self.__capacity):
                    if not self.__wait_queue.empty():
                        next = self.__wait_queue.get()
                        next.update_status(False)
                        self.__on_ride_list.put(next)
                        self.__line_length -= 1
                        self.__on_ride_length += 1
                    else:
                        break
            hold = (int((self.__on_ride_length / 2)) + 1)  #holds how long it took to put customers onto the ride
            if self.__on_ride_length % 2 == 1 and self.__current_active_time == 0 and self.__setting_up:
                self.__set_up_time = ((hold + 1) * 3) + rand_set  #carts + worker setup
            elif self.__on_ride_length % 2 == 0 and self.__current_active_time == 0 and self.__setting_up:
                self.__set_up_time = (self.__on_ride_length / 2) + rand_set
            self.__set_up_time = int(self.__set_up_time)
            #  Increments the time for the setup of the ride
            if self.__setting_up:
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__set_up_time:
                    self.__current_active_time = 0
                    self.__setting_up = False
                    self.__active = True
            #  Increments the time for the ride while it is active
            elif self.is_active():
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__ride_time:
                    self.__current_active_time = 0
                    self.__active = False
                    self.__leaving = True
                    self.__leave_time = int(rand_leave)
            #  Increments the time while the riders are exiting the ride
            elif self.__leaving:
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__leave_time:
                    self.__current_active_time = 0
                    self.__times_ran += 1
                    self.__leaving = False
                    self.__setting_up = True
                    while not self.__on_ride_list.empty():
                        rider = self.__on_ride_list.get()
                        rider.update_status(True)
                        move_list.put(rider)
                        self.__on_ride_length -= 1
        # -------------------------------------------------------------------------------------------------------------
        # Identical to the top but if the ride is the merry-go-round
        if not self.__is_coaster:
            rand_leave_merry = numpy.random.normal(30, 5)
            if self.__setting_up and self.__on_ride_length == 0:
                for x in range(0, self.__capacity):
                    if not self.__wait_queue.empty():
                        next = self.__wait_queue.get()
                        next.update_status(False)
                        self.__on_ride_list.put(next)
                        self.__line_length -= 1
                        self.__on_ride_length += 1
                    else:
                        break
                hold = numpy.random.normal(120, 15)
                self.__set_up_time = int(hold)
            if self.__setting_up:
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__set_up_time:
                    self.__current_active_time = 0
                    self.__setting_up = False
                    self.__active = True
            elif self.is_active():
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__ride_time:
                    self.__current_active_time = 0
                    self.__active = False
                    self.__leaving = True
                    self.__leave_time = int(rand_leave_merry)
            elif self.__leaving:
                self.__current_active_time += 1
                self.__start_to_finish += 1
                if self.__current_active_time == self.__leave_time:
                    self.__current_active_time = 0
                    self.__times_ran += 1
                    self.__leaving = False
                    self.__setting_up = True
                    while not self.__on_ride_list.empty():
                        rider = self.__on_ride_list.get()
                        rider.update_status(True)
                        move_list.put(rider)
                        self.__on_ride_length -= 1
        return move_list

