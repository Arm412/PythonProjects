import queue
import numpy
import random
import math
import sys
from Cash_booths import Cash_booths
from Customer import Customer
from Ride import Ride

g_avg_attendance = 0
g_avg_coaster_length = 0
g_avg_merry_length = 0
g_avg_express_length = 0
g_avg_cash_length = 0
g_wait_avg_coaster = 0
g_wait_avg_merry = 0
g_wait_avg_express = 0
g_wait_avg_cash = 0
g_ticket_waste_avg = 0
g_avg_profit = 0
g_idle_express = 0
g_idle_cash = 0
g_idle_coaster = 0
g_idle_merry = 0
g_idle_game = 0
def main(merry_capacity):
    global unused_tickets
    global total_customers_atm
    global total_cash
    global total_game_capacity
    global g_avg_attendance
    global g_avg_coaster_length
    global g_avg_merry_length
    global g_avg_express_length
    global g_avg_cash_length
    global g_wait_avg_coaster
    global g_wait_avg_merry
    global g_wait_avg_express
    global g_wait_avg_cash
    global g_ticket_waste_avg
    global g_avg_profit
    global workers_idle
    global g_idle_express
    global g_idle_cash
    global g_idle_coaster
    global g_idle_merry
    global g_idle_game
    total_customers = 0
    # ---------------------------------
    line_length1 = 0
    line_length2 = 0
    line_length3 = 0
    line_length4 = 0
    wait1 = 0
    wait2 = 0
    wait3 = 0
    wait4 = 0
    # --------------------------------- This section used for metrics
    quarter = 0
    early_list = {}
    capacity = merry_capacity
    roller_coaster = Ride(16, 60, 3, 180, 30, True)
    merry_go_round = Ride(8, capacity, 120, 240, 30, False)
    game_slots = []
    express_line = Cash_booths(True)
    cash_line = Cash_booths(False)
    avg_customers = 0
    # creates the  early customers
    x = 0
    hours = 0
    customer_queue = queue.Queue(500)
    waiting = queue.Queue(500)
    no_more_entry = False
    # Use a Normal Distribution to find number of early arrivals
    numb_of_early_customers = int(numpy.random.normal(200, 10))
    while x < numb_of_early_customers:
        numb = int(numpy.random.normal(1800, 900))
        try:
            if early_list[numb]:
                continue
        except KeyError:
            if numb < 1 or numb > 3600:
                continue
            else:
                early_list[numb] = True
        x += 1
    # This boolean var is used to determine if the initial crowd queue was dealt with when it opens
    initial_wait = True
    new_arrival = -1
    for x in range(1, 30601):
        if x <= 3600:
            if is_open(x) and initial_wait:
                move_to_cash_booths(customer_queue, express_line, cash_line)
                initial_wait = False
            try:
                # This will hold the early customers who arrived before it opens
                if early_list[x] and initial_wait:
                    customer_queue.put(Customer(True))
                    total_customers_atm += 1
                    total_customers += 1
                elif early_list[x]:
                    send_to_tickets(Customer(True), express_line, cash_line)
                    total_customers_atm += 1
                    total_customers += 1
            except KeyError:
                continue
        if x == 3601:
            new_arrival = numpy.random.poisson(240) + x
        if new_arrival == x and not no_more_entry:
            total_customers_atm += 1
            total_customers += 1
            send_to_tickets(Customer(False), express_line, cash_line)
            new_arrival = numpy.random.poisson(240) + x
        elif x == 25200:
            no_more_entry = True
        express_line.update(waiting)
        cash_line.update(waiting)
        leaving = roller_coaster.update()
        move(leaving, roller_coaster, merry_go_round, game_slots)
        leaving = merry_go_round.update()
        move(leaving, roller_coaster, merry_go_round, game_slots)
        update_games(game_slots, waiting)
        move(waiting, roller_coaster, merry_go_round, game_slots)

        # Check every hour for total customers at the fair
        if x % 3600 == 0 and not x == 3600:
            avg_customers += total_customers_atm
            hours += 1
        if x % 900 and x > 3601:
            line_length1 += express_line.get_length()
            line_length2 += cash_line.get_length()
            line_length3 += roller_coaster.get_line_length()
            line_length4 += merry_go_round.get_line_length()
            wait1 += express_line.get_time()
            wait2 += cash_line.get_time()
            wait3 += math.ceil(roller_coaster.get_line_length()/roller_coaster.get_capacity()) * 290
            wait4 += math.ceil(merry_go_round.get_line_length()/merry_go_round.get_capacity()) * 390
            quarter += 1

    leftover_tickets = 0
    leftover_tickets += get_ride_leftovers(roller_coaster)
    leftover_tickets += get_ride_leftovers(merry_go_round)
    leftover_tickets += get_game_leftovers(game_slots)

    wage = 10
    coaster_operator = 1
    merry_operator = 1
    games_operator = math.ceil(total_game_capacity/5)
    cashier = 1
    cost = 0
    cost += wage * (coaster_operator + merry_operator + games_operator + cashier) * hours
    cost -= 20  # Cashier doesnt get 1 hour worth of pay at the end

    if merry_go_round.get_capacity() == 30:  # If we got a bigger carousel
        total_cash -= 5000

    if not total_game_capacity == 50:
        stalls_sold = 10 - math.ceil(total_game_capacity/5)
        total_cash += stalls_sold * 200  # $200 per stall sold

    g_avg_attendance += int(avg_customers/hours)
    g_avg_express_length += int(line_length1/quarter)
    g_avg_cash_length += int(line_length2 / quarter)
    g_avg_coaster_length += int(line_length3 / quarter)
    g_avg_merry_length += int(line_length4 / quarter)
    g_wait_avg_coaster += int(wait3/quarter)
    g_wait_avg_merry += int(wait4/quarter)
    g_wait_avg_express += int(wait1 / quarter)
    g_wait_avg_cash += int(wait2 / quarter)
    g_ticket_waste_avg += leftover_tickets
    g_avg_profit += total_cash-cost
    g_idle_express += express_line.get_worker_idle_time()
    g_idle_cash += cash_line.get_worker_idle_time()
    g_idle_coaster += roller_coaster.get_worker_idle_time()
    g_idle_merry += merry_go_round.get_worker_idle_time()
    g_idle_game += workers_idle




def get_ride_leftovers(ride):
    tickets = 0
    while not ride.get_wait_queue().empty():
        c = ride.get_wait_queue().get()
        tickets += c.get_tickets()
    while not ride.get_on_ride_queue().empty():
        c = ride.get_on_ride_queue().get()
        tickets += c.get_tickets()
    return tickets

def get_game_leftovers(stalls):
    x = 0
    tickets = 0
    while x < len(stalls):
        tickets += stalls[x].get_tickets()
        x += 1
    return tickets



def is_open(seconds):
    if seconds >= 1800:
        return True
    else:
        return False

# This method will be used with the early arrivals
# Takes the initial crowd and sends them to the tickets lines
def move_to_cash_booths(queue, express, cash):
    global total_cash
    while not queue.empty():
        probability = int(random.random()*100)
        if probability <= 80:
            c = queue.get()
            add_to_express(express, c)
        else:
            if cash.get_time() > 1200 and cash.get_length() > express.get_length() * 2:
                prob_of_switch = int(random.Random()*100)
                if prob_of_switch <= 20:
                    c = queue.get()
                    add_to_express(express, c)
                else:
                    c = queue.get()
                    cash.add_to_queue(c)
                    get_cash_tickets(cash, c)
            else:
                c = queue.get()
                cash.add_to_queue(c)
                get_cash_tickets(cash, c)

def add_to_express(express, c):
    global total_cash
    express.add_to_queue(c)
    express.add_time(15)
    c.set_time(15)
    c.add_tickets(200)
    total_cash += 50
    c.update_status(True)

def send_to_tickets(customer, express, cash):
    global total_cash
    probability = int(random.random() * 100)
    express_line_prob = 0
    if customer.is_early():
        express_line_prob = 80
    else:
        express_line_prob = 10
    if probability <= express_line_prob:
        add_to_express(express, customer)
    else:
        if cash.get_time() > 1200 and cash.get_length() > express.get_length() * 2:
            prob_of_switch = int(random.random() * 100)
            if prob_of_switch <= 20:
                add_to_express(express, customer)
            else:
                cash.add_to_queue(customer)
                get_cash_tickets(cash, customer)
        else:
            cash.add_to_queue(customer)
            get_cash_tickets(cash, customer)

def get_cash_tickets(line, customer):
    global total_cash
    tickets = numpy.random.normal(100, 30)
    time = int((tickets * .1) + numpy.random.normal(120, 15))
    customer.set_time(time)
    line.add_time(time)
    customer.add_tickets(int(tickets))
    total_cash += .25 * int(tickets)
    customer.update_status(True)
    return time

def move(list_of_waiting, roller_coaster, merry_go_round, game_slots):
    global total_game_capacity
    global unused_tickets
    global total_customers_atm
    while not list_of_waiting.empty():
        coaster = 0
        games = 0
        merry = 0
        customer = list_of_waiting.get()
        if customer.get_tickets() >= 16:
            coaster = 40
            games = 35
            merry = 25
        elif customer.get_tickets() >= 8:
            games = 58
            merry = 42
        elif customer.get_tickets() >= 1:
            if len(game_slots) == total_game_capacity:
                #print("Customer leaves park with {} tickets".format(customer.get_tickets()))
                unused_tickets += customer.get_tickets()
                total_customers_atm -= 1
                continue
            games = 100
        else:
            total_customers_atm -= 1
            continue
        while True:
            prob = random.random() * 100
            if prob <= coaster:
                customer.update_status(True)
                customer.remove_tickets(16)
                roller_coaster.add_rider(customer)
                break
            elif prob <= coaster + merry:
                customer.update_status(True)
                customer.remove_tickets(8)
                merry_go_round.add_rider(customer)
                break
            elif prob <= coaster + merry + games:
                if len(game_slots) < total_game_capacity:
                    customer.update_status(True)
                    customer.remove_tickets(1)
                    time = numpy.random.normal(30, 5)
                    customer.set_time(int(time))
                    game_slots.append(customer)
                    break
                else:
                    continue

def update_games(games_slots, waiting):
    global workers_idle
    if len(games_slots) + 5 < total_game_capacity:
        workers_idle += 1
    length = len(games_slots)
    if length == 0:
        return
    index = 0
    while not index == length:
        customer = games_slots[index]
        customer.update_time()
        if customer.get_time() == 0:
            games_slots.remove(customer)
            index -= 1
            length -= 1
            waiting.put(customer)
        index += 1


days = 1
stall_capacity = int(input("How many game stalls are there? "))
merry_go_round_capacity = int(input("How many people can fit on the Merry-Go-Round? "))
print("------------------------------------------------------------------------------------------------------")
for day in range(0, days):
    game_capacity = stall_capacity
    total_cash = 0
    total_customers_atm = 0
    unused_tickets = 0
    total_game_capacity = game_capacity
    workers_idle = 0
    main(merry_go_round_capacity)
print("Attendance Average: {}".format(int(g_avg_attendance/days)))
print("Average Line Length (Express): {}".format(int(g_avg_express_length/days)))
print("Average Line Length (Cash): {}".format(int(g_avg_cash_length/days)))
print("Average Line Length (Coaster): {}".format(int(g_avg_coaster_length/days)))
print("Average Line Length (Merry): {}".format(int(g_avg_merry_length/days)))
print("Average Wait Time (Express): {}".format(int(g_wait_avg_express/days)))
print("Average Wait Time (Cash): {}".format(int(g_wait_avg_cash/days)))
print("Average Wait Time (Coaster): {}".format(int(g_wait_avg_coaster/days)))
print("Average Wait Time (Merry): {}".format(int(g_wait_avg_merry/days)))
print("Average Amount of Tickets Wasted: {}".format(int(g_ticket_waste_avg/days)))
print("Average Profit: {:,.2f}".format(g_avg_profit/days))
print("Average Idle Worker Time (Express): {}".format(int(g_idle_express/days)))
print("Average Idle Worker Time (Cash): {}".format(int(g_idle_cash/days)))
print("Average Idle Worker Time (Coaster): {}".format(int(g_idle_coaster/days)))
print("Average Idle Worker Time (Merry): {}".format(int(g_idle_merry/days)))
print("Average Idle Worker Time (Game - At least one): {}".format(int(g_idle_game/days)))