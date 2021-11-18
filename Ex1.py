# Noah Weiss: 326876786
# Rashi Pachino: 345174478

import sys
import csv
import json
from math import ceil
from typing import List


class Building:
    def __init__(self, elevators: list, min_floor: int, max_floor: int):  # constructor for building
        self.elevators = elevators
        self.min_floor = min_floor
        self.max_floor = max_floor


class Elevator:
    def __init__(self, d: dict):  # constructor for elevator
        self.id = d.get("_id")
        self.speed = d.get("_speed")
        self.min_floor = d.get("_minFloor")
        self.max_floor = d.get("_maxFloor")
        self.close_time = d.get("_closeTime")
        self.open_time = d.get("_openTime")
        self.start_time = d.get("_startTime")
        self.stop_time = d.get("_stopTime")

    def __str__(self):  # returns string of the elevator as a dictionary
        return str({"_id": self.id, "_speed": + self.speed, "_minFloor": self.min_floor, "_maxFloor": self.max_floor, "_closeTime": self.close_time, "_openTime": self.open_time, "_startTime": self.start_time, "_stopTime": self.stop_time})


class CallForElevator:
    def __init__(self, call: list):  # constructor for call for elevator
        self.time = float(call[1])
        self.src = int(call[2])
        self.dest = int(call[3])
        self.allocated_to = int(call[5])

    def call_as_list(self) -> list:  # returns the call in the format of a list
        return ["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to]

    def __str__(self) -> str:  # returns string of the call for elevator as a list
        return str(["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to])


def time_floor2floor(elev: Elevator, a: int, b: int) -> float:  # returns how long it takes to get from floor a to floor b
    if a == b:  # if floors are the same
        return 0
    return elev.close_time + elev.start_time + ceil((abs(a-b)/elev.speed)) + elev.stop_time + elev.open_time


def pos_in_range(elev: Elevator, going_from: int, going_to: int, q_time: float, t_time: float) -> int:  # returns what the exact position of the elevator will be at a given time between two given floors
    if going_to == going_from:
        return going_to
    sec_per_floor = ceil(abs(going_from - going_to) / elev.speed) / abs(going_from - going_to)  # how many seconds the elevator spends at an in between floor
    floor = going_from
    t_time += elev.close_time + elev.start_time  # add the start ad close times
    if t_time >= q_time:  # if we passed the desired time return the floor
        return floor
    for fl in range(abs(going_from - going_to)):  # now going through in-between floors
        if going_from < going_to:  # elevator is going up
            floor += 1  # 'pos' increases by one
        else:  # elevator is going down
            floor -= 1  # 'pos' decreases by one
        t_time += sec_per_floor
        if t_time >= q_time:  # if we passed the desired time return the floor
            return floor
    return going_to


def pos_at_time(elev: Elevator, elev_call_list: List[dict], time: float) -> int:  # returns what the position of the elevator will be at the given time
    if len(elev_call_list) == 0:  # if the list is empty the the elevator is still at floor 0 (the starting position)
        return 0
    query_time = ceil(time)  # round up the call time beacuse the simulator only will act on it at the next time stamp which is at every full 'second'
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))  # add the gap in time until the first call was placed
    if query_time < total_time:
        return pos_in_range(elev, 0, elev_call_list[0].get("floor"), query_time, total_time)
    for i in range(len(elev_call_list)-1):  # go through the elev call list
        if total_time < ceil(elev_call_list[i+1].get("call").time):  # if there is a gap until the next call
            if query_time <= ceil(elev_call_list[i+1].get("call").time):
                return elev_call_list[i].get("floor")
            total_time = ceil(elev_call_list[i+1].get("call").time)  # jump to the time of the call after the gap
        elif query_time < total_time + time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor")):  # if we passed the time we are searching for return
            return pos_in_range(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"), query_time, total_time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))  # add the time it takes to get to the next floor
    return elev_call_list[-1].get("floor")


def future_call_list(elev: Elevator, elev_call_list: List[dict], time: float) -> int:  # returns the index of the first floor of what the elevators call list will look like at the given time
    if len(elev_call_list) == 0:  # if the list is empty the the elevator is still at floor 0 (the starting position)
        return -1
    query_time = ceil(time)  # round up the call time beacuse the simulator only will act on it at the next time stamp which is at every full 'second'
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))  # add the gap in time until the first call was placed
    if query_time < total_time:
        return 0
    for i in range(len(elev_call_list)-1):  # go through the elev call list
        if total_time < ceil(elev_call_list[i+1].get("call").time):  # if there is a gap until the next call
            total_time = ceil(elev_call_list[i+1].get("call").time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))  # add the time it takes to get to the next floor on the list
        if query_time < total_time:  # if we passed the time we are searching for return the next index
            return i+1
    return len(elev_call_list)


def time_to_complete_call(call: CallForElevator, elev_call_list: List[dict], elev: Elevator, dest_ind: int) -> float:  # returns the time it takes to complete a call
    return time_at_index(elev_call_list, dest_ind, elev) - call.time


def time_at_index(elev_call_list: List[dict], index: int, elev: Elevator) -> float:  # returns the time it will be at a certain index on the call list
    if len(elev_call_list) == 0:
        return 0
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))  # add the gap in time until the first call was placed
    for i in range(index):  # go though the elev call list until the given index
        if total_time < ceil(elev_call_list[i+1].get("call").time):  # if there is a gap until the next call
            total_time = ceil(elev_call_list[i+1].get("call").time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))  # add the time it takes to get to the next floor on the list
    return total_time


def add_call_to_elevator_bank(call: CallForElevator, elev: Elevator, elev_call_list: List[dict]) -> int:  # adds call src and dest to the elevator's call list and returns what the index is of where the the dest was inserted in the call list
    index = future_call_list(elev, elev_call_list, call.time)  # gets what the elevator's call list will look like at the call time
    pos = pos_at_time(elev, elev_call_list, call.time)  # gets what the position of the elevator will be at the time of the call
    src_index = add_floor(call.src, elev_call_list, index, call, pos)  # adds the src to the call list and return the index of where it was inserted
    return add_floor(call.dest, elev_call_list, src_index+1, call, call.src)  # adds the dest to the call list and returns the index of where it was inserted


def add_floor(floor: int, elev_call_list: List[dict], index: int, call: CallForElevator, pos) -> int:  # adds given floor to the elevator's call list and returns the index of where it was inserted
    if index == -1:  # if the list is empty
        elev_call_list.append({"floor": floor, "call": call})
        return 0
    if index == len(elev_call_list):  # if the index equals the len then the future list is empty at the time the call came in so add the floor to the end
        elev_call_list.append({"floor": floor, "call": call})
        return index
    if index == 1 and (floor < elev_call_list[0].get("floor") < 0 or floor > elev_call_list[0].get("floor") > 0):  # if the index is 1 and the elevator is going in a certain direction and my floor is in the same direction then insert the floor at 1
        elev_call_list.insert(1, {"floor": floor, "call": call})
        return 1
    if (elev_call_list[index-2].get("floor") < elev_call_list[index-1].get("floor") < floor and elev_call_list[index-1].get("floor") > elev_call_list[index].get("floor") and elev_call_list[index-1].get("floor") == pos) or (elev_call_list[index-2].get("floor") > elev_call_list[index-1].get("floor") > floor and elev_call_list[index-1].get("floor") < elev_call_list[index].get("floor") and elev_call_list[index-1].get("floor") == pos):  # if the elevator is going in a certain direction and my floor is in the same direction then add the floor there
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    direction = "UP" if elev_call_list[index-1].get("floor") < elev_call_list[index].get("floor") else "DOWN"
    if (direction == "UP" and pos < floor < elev_call_list[index].get("floor")) or (direction == "DOWN" and pos > floor > elev_call_list[index].get("floor")):  # if the floor can be stopped on the way to where its going at the time of the call
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    for i in range(index, len(elev_call_list) - 1):  # go through the elevator call list from the index until the end and check where the floor can be inserted according to the elevator algorithm
        if elev_call_list[i].get("floor") != elev_call_list[i+1].get("floor"):
            next_direction = "UP" if elev_call_list[i].get("floor") < elev_call_list[i+1].get("floor") else "DOWN"
            if direction == "UP" and next_direction == "UP" and elev_call_list[i].get("floor") < floor < elev_call_list[i+1].get("floor"):
                elev_call_list.insert(i+1, {"floor": floor, "call": call})
                return i+1
            if direction == "UP" and next_direction == "DOWN" and (floor > elev_call_list[i].get("floor") or elev_call_list[i].get("floor") > floor > elev_call_list[i+1].get("floor")):
                elev_call_list.insert(i+1, {"floor": floor, "call": call})
                return i+1
            if direction == "DOWN" and next_direction == "DOWN" and elev_call_list[i].get("floor") > floor > elev_call_list[i+1].get("floor"):
                elev_call_list.insert(i+1, {"floor": floor, "call": call})
                return i+1
            if direction == "DOWN" and next_direction == "UP" and (floor < elev_call_list[i].get("floor") or elev_call_list[i].get("floor") < floor < elev_call_list[i+1].get("floor")):
                elev_call_list.insert(i+1, {"floor": floor, "call": call})
                return i+1
            direction = next_direction
    elev_call_list.append({"floor": floor, "call": call})
    return len(elev_call_list) - 1


def fastest_elev(building: Building, call: CallForElevator, calls_bank: dict) -> int:  # returns the elevator id of the elevator that offers the shortest time to complete the given call
    ans = 0  # assume the answer is elevator 0
    temp_elev_call_list = []
    for floor in calls_bank[building.elevators[0].id]:  # move all of the floor calls to a temp list so it doesnt affect the real list
        temp_elev_call_list.append(floor)
    dest_ind = add_call_to_elevator_bank(call, building.elevators[0], temp_elev_call_list)  # add the call to the temp list
    min_time = time_to_complete_call(call, temp_elev_call_list, building.elevators[0], dest_ind)  # check how long it takes for this elevator to complete this call
    for elev in building.elevators[1:]:  # check the rest of the elevators
        temp_elev_call_list = []
        for floor in calls_bank[elev.id]:
            temp_elev_call_list.append(floor)
        dest_ind = add_call_to_elevator_bank(call, elev, temp_elev_call_list)  # add the call to the temp list
        time = time_to_complete_call(call, temp_elev_call_list, elev, dest_ind)  # check how long it takes for this elevator to complete this call
        if time < min_time:  # if the time this elevator offers is smaller than the min time
            min_time = time
            ans = elev.id
    return ans


def on_the_way(building: Building, call: CallForElevator, calls_bank: dict) -> int:  # returns the first elevator that has the given calls src and dest already on its call list at the time of the call
    for elev in building.elevators:  # go through all of the elevators
        index = future_call_list(elev, calls_bank[elev.id], call.time)  # get the index of the beggining of the future call list at the time of the call
        if index != -1:
            for i in range(index, len(calls_bank[elev.id])):  # go through all of the calls from starting from index
                if calls_bank[elev.id][i].get("floor") == call.src:  # if the src is found
                    for k in range(i, len(calls_bank[elev.id])):  # check if the dest is found sometime after the src
                        if calls_bank[elev.id][k].get("floor") == call.dest:  # if it does then return the id of this elevator
                            return elev.id
    return -1  # if not found return -1


if __name__ == '__main__':

    # get building info from json
    with open(sys.argv[1], "r") as j:  # in order to take all of the elevators from the json
        reader = json.load(j)
        min_floor = reader.get("_minFloor")
        max_floor = reader.get("_maxFloor")
        elevs = reader.get("_elevators")

    elev_list = [Elevator(elev) for elev in elevs]  # take every 'elevator' and turn it into an object of type Elevator
    building = Building(elev_list, min_floor, max_floor)  # make a building out of the elevator list and max/min floors of the building

    # get calls info from csv
    with open(sys.argv[2], "r") as c:  # in order to take all of the elevator calls from csv
        reader = csv.reader(c)
        calls_list = [CallForElevator(line) for line in reader]  # take every 'call' and turn it into an object of type CallForElevator

    elevator_floor_calls_bank = {}  # dictionary that will keep track of floor calls for all of the elevators
    for i in building.elevators:
        elevator_floor_calls_bank[i.id] = []

    for call in calls_list:  # go through every call in the calls list and give an allocation
        otw_id = on_the_way(building, call, elevator_floor_calls_bank)  # check if there is an elevator that has the call src and dest on its way
        if otw_id != -1:
            ans = otw_id
        else:
            fastest_id = fastest_elev(building, call, elevator_floor_calls_bank)  # find the elevator that can finish the call in the shortest time
            ans = fastest_id
        call.allocated_to = ans
        add_call_to_elevator_bank(call, building.elevators[ans], elevator_floor_calls_bank[ans])  # add the call to the elevators call list

    # write updated calls to a new file
    with open(sys.argv[3], "w") as c:
        writer = csv.writer(c)
        for call in calls_list:
            writer.writerow(call.call_as_list())
