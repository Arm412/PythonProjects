import queue
from Customer import Customer

class Cash_booths:
    def __init__(self, express_line):
        self.__express = express_line
        self.__queue_length = 0
        self.__active_customer = 0
        self.__transaction_time = 0
        self.__countdown = 0
        self.__worker_waiting = 0
        if self.__express:
            self.__min_tickets = 200
            self.__cost = 50
        else:
            self.__min_tickets = 1
            self.__cost = .25
        self.__queue = queue.Queue(2000)

    # returns the next in line
    def next(self):
        self.__queue_length -= 1
        next_customer = self.__queue.get()
        next_customer.update_status(False)
        return next_customer

    def is_empty(self):
        return self.__queue.empty()

    def get_worker_idle_time(self):
        return self.__worker_waiting

    def add_to_queue(self, customer):
        self.__queue.put(customer)
        self.__queue_length += 1
    def get_length(self):
        return self.__queue_length

    def get_time(self):
        return self.__transaction_time

    def update(self, customers_awaiting_placement):
        if self.__active_customer == 0 and self.__queue_length > 0:  # If no customer currently in booth, take from the queue
            self.__active_customer = self.next()
        elif self.__active_customer != 0:
            self.__transaction_time -= 1
            self.__active_customer.update_time()
            if self.__active_customer.get_time() == 0:
                # acquire_tickets
                customers_awaiting_placement.put(self.__active_customer)
                if self.__queue_length > 0:
                    self.__active_customer = self.next()
                else:
                    self.__active_customer = 0
        else:
            self.__worker_waiting += 1
            return

    def add_time(self, time):
        self.__transaction_time += time

    def get_customer(self):
        return self.__active_customer