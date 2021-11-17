# Noah Weiss: 326876786
# Rashi Pachino: 345174478

import sys
import csv
import json
from math import ceil
from typing import List


class Building:
    def __init__(self, elevators: list, min_floor: int, max_floor: int):
        self.elevators = elevators
        self.min_floor = min_floor
        self.max_floor = max_floor


class Elevator:
    def __init__(self, d: dict):
        self.id = d.get("_id")
        self.speed = d.get("_speed")
        self.min_floor = d.get("_minFloor")
        self.max_floor = d.get("_maxFloor")
        self.close_time = d.get("_closeTime")
        self.open_time = d.get("_openTime")
        self.start_time = d.get("_startTime")
        self.stop_time = d.get("_stopTime")
        self.pos = 0

    def __str__(self):
        return str({"_id": self.id, "_speed": + self.speed, "_minFloor": self.min_floor, "_maxFloor": self.max_floor, "_closeTime": self.close_time, "_openTime": self.open_time, "_startTime": self.start_time, "_stopTime": self.stop_time})


class CallForElevator:
    def __init__(self, call: list):
        self.time = float(call[1])
        self.src = int(call[2])
        self.dest = int(call[3])
        self.allocated_to = int(call[5])
        self.direction = self.dest > self.src

    def call_as_list(self) -> list:
        return ["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to]

    def __str__(self) -> str:
        return str(["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to])


def time_floor2floor(elev: Elevator, a: int, b: int) -> float:
    if a == b:
        return 0
    return elev.close_time + elev.start_time + ceil((abs(a-b)/elev.speed)) + elev.stop_time + elev.open_time


def pos_in_range(elev: Elevator, going_from: int, going_to: int, q_time: float, t_time: float) -> int:
    if going_to == going_from:
        return going_to
    sec_per_floor = ceil(abs(going_from - going_to) / elev.speed) / abs(going_from - going_to)
    floor = going_from
    t_time += elev.close_time + elev.start_time
    if t_time >= q_time:
        return floor
    for fl in range(abs(going_from - going_to)):  # now going through in-between floors
        if going_from < going_to:  # elevator is going up
            t_time += sec_per_floor
            floor += 1  # 'pos' increases by one
        else:  # elevator is going down
            t_time += sec_per_floor
            floor -= 1  # 'pos' decreases by one
        if t_time >= q_time:
            return floor
    return going_to


def future_call_list(elev: Elevator, elev_call_list: List[dict], time: float) -> int:
    if len(elev_call_list) == 0:
        return -1
    query_time = ceil(time)
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))
    if query_time < total_time:
        return 0
    for i in range(len(elev_call_list)-1):
        if total_time < ceil(elev_call_list[i+1].get("call").time):
            total_time = ceil(elev_call_list[i+1].get("call").time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))
        if query_time < total_time:
            return i+1
    return len(elev_call_list)


def pos_at_time(elev: Elevator, elev_call_list: List[dict], time: float) -> int:
    if len(elev_call_list) == 0:
        return 0
    query_time = ceil(time)
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))
    if query_time < total_time:
        return pos_in_range(elev, 0, elev_call_list[0].get("floor"), query_time, total_time)
    for i in range(len(elev_call_list)-1):
        if total_time < ceil(elev_call_list[i+1].get("call").time):
            if query_time <= ceil(elev_call_list[i+1].get("call").time):
                return elev_call_list[i].get("floor")
            total_time = ceil(elev_call_list[i+1].get("call").time)
        elif query_time < total_time + time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor")):
            return pos_in_range(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"), query_time, total_time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))
    return elev_call_list[-1].get("floor")


def time_to_complete_call(call: CallForElevator, elev_call_list: List[dict], elev: Elevator, dest_ind: int) -> float:
    return time_at_index(elev_call_list, dest_ind, elev) - call.time


def time_at_index(elev_call_list: List[dict], index: int, elev: Elevator) -> float:
    if len(elev_call_list) == 0:
        return 0
    total_time = ceil(elev_call_list[0].get("call").time) + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))
    for i in range(index):
        if total_time < ceil(elev_call_list[i+1].get("call").time):
            total_time = ceil(elev_call_list[i+1].get("call").time)
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))
    return total_time


def add_call_to_elevator_bank(call: CallForElevator, elev: Elevator, elev_call_list: List[dict]) -> int:  # adds call src and dest to the elevators call list
    index = future_call_list(elev, elev_call_list, call.time)
    pos = pos_at_time(elev, elev_call_list, call.time)
    src_index = add_floor(call.src, elev_call_list, index, call, pos)
    return add_floor(call.dest, elev_call_list, src_index+1, call, call.src)


def add_floor(floor: int, elev_call_list: List[dict], index: int, call: CallForElevator, pos) -> int:  # adds floor to the elevators call list
    if index == -1:
        elev_call_list.append({"floor": floor, "call": call})
        return 0
    if index == len(elev_call_list):
        elev_call_list.append({"floor": floor, "call": call})
        return index
    if index == 1 and (floor < elev_call_list[0].get("floor") < 0 or floor > elev_call_list[0].get("floor") > 0):
        elev_call_list.insert(1, {"floor": floor, "call": call})
        return 1
    if (elev_call_list[index-2].get("floor") < elev_call_list[index-1].get("floor") < floor and elev_call_list[index-1].get("floor") > elev_call_list[index].get("floor") and elev_call_list[index-1].get("floor") == pos) or (elev_call_list[index-2].get("floor") > elev_call_list[index-1].get("floor") > floor and elev_call_list[index-1].get("floor") < elev_call_list[index].get("floor") and elev_call_list[index-1].get("floor") == pos):
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    direction = "UP" if elev_call_list[index-1].get("floor") < elev_call_list[index].get("floor") else "DOWN"
    if (direction == "UP" and pos < floor < elev_call_list[index].get("floor")) or (direction == "DOWN" and pos > floor > elev_call_list[index].get("floor")):
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    for i in range(index, len(elev_call_list) - 1):
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


def fastest_elev(building: Building, call: CallForElevator, calls_bank: dict) -> (int, float):
    ans = 0
    temp_elev_call_list = []
    for floor in calls_bank[building.elevators[0].id]:
        temp_elev_call_list.append(floor)
    dest_ind = add_call_to_elevator_bank(call, building.elevators[0], temp_elev_call_list)
    min_time = time_to_complete_call(call, temp_elev_call_list, building.elevators[0], dest_ind)
    for elev in building.elevators[1:]:
        temp_elev_call_list = []
        for floor in calls_bank[elev.id]:
            temp_elev_call_list.append(floor)
        dest_ind = add_call_to_elevator_bank(call, elev, temp_elev_call_list)
        time = time_to_complete_call(call, temp_elev_call_list, elev, dest_ind)
        if time < min_time:
            min_time = time
            ans = elev.id
    return ans, min_time


def on_the_way(building: Building, call: CallForElevator, calls_bank: dict) -> int:
    for elev in building.elevators:
        pos = future_call_list(elev, calls_bank[elev.id], call.time)
        if pos != -1:
            for i in range(pos, len(calls_bank[elev.id])):
                if calls_bank[elev.id][i].get("floor") == call.src:
                    for k in range(i, len(calls_bank[elev.id])):
                        if calls_bank[elev.id][k].get("floor") == call.dest:
                            return elev.id
    return -1


if __name__ == '__main__':

    # get building from json
    with open(sys.argv[1], "r") as j:  # in order to take all of the elevators from the json
        reader = json.load(j)
        min_floor = reader.get("_minFloor")
        max_floor = reader.get("_maxFloor")
        elevs = reader.get("_elevators")

    elev_list = [Elevator(elev) for elev in elevs]
    building = Building(elev_list, min_floor, max_floor)

    # get calls from csv
    with open(sys.argv[2], "r") as c:  # in order to take all of the elevator calls from csv
        reader = csv.reader(c)
        calls_list = [CallForElevator(line) for line in reader]

    elevator_calls_bank = {}
    elevator_floor_calls_bank = {}
    for i in building.elevators:
        elevator_calls_bank[i.id] = []
        elevator_floor_calls_bank[i.id] = []

    for call in calls_list:
        otw_id = on_the_way(building, call, elevator_floor_calls_bank)
        if otw_id != -1:
            ans = otw_id
        else:
            fastest_id, fastest_time = fastest_elev(building, call, elevator_floor_calls_bank)
            ans = fastest_id
        call.allocated_to = ans
        elevator_calls_bank[ans].append(call)
        add_call_to_elevator_bank(call, building.elevators[ans], elevator_floor_calls_bank[ans])

    # write updated calls to a new file
    with open(sys.argv[3], "w") as c:
        writer = csv.writer(c)
        for call in calls_list:
            writer.writerow(call.call_as_list())