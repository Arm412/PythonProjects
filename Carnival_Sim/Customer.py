class Customer:
    def __init__(self, early):
        self.__tickets = 0
        self.__waiting = False
        self.__early = early
        self.__transaction_time = 0
        self.__game_time = 0

    def add_tickets(self, ticket_amt):
        self.__tickets += ticket_amt

    def remove_tickets(self, ticket_amt):
        self.__tickets -= ticket_amt

    def get_tickets(self):
        return self.__tickets

    def get_status(self):
        return self.__waiting

    def update_status(self, status):
        self.__waiting = status
    def is_early(self):
        return self.__early

    def set_time(self, time):
        self.__transaction_time = time

    def update_time(self):
        self.__transaction_time -= 1

    def get_time(self):
        return self.__transaction_time
