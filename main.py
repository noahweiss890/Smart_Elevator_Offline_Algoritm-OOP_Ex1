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

    def time_to_complete_call(self, elev: Elevator) -> float:
        return 1 - (self.time - int(self.time)) + elev.close_time + elev.start_time + ceil(abs(self.src - self.dest) / elev.speed) + elev.stop_time + elev.open_time

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
    floor = going_from
    t_time += elev.close_time  # first add close_time and see if that makes a difference
    if t_time >= q_time:
        return floor
    t_time += elev.start_time
    # elevator already started so now can only stop at next floor up or down depending on direction
    if t_time >= q_time and (going_from < going_to):  # elevator is going up
        return floor + 1
    if t_time >= q_time and (going_from > going_to):  # elevator is going down
        return floor - 1
    for fl in range(abs(going_from - going_to)):  # now going through in-between floors
        if going_from < going_to:  # elevator is going up
            t_time += (1/elev.speed)
            floor += 1  # 'pos' increases by one
        if going_from > going_to:  # elevator is going down
            t_time += (1/elev.speed)
            floor -= 1  # 'pos' decreases by one
        if t_time >= q_time:
            return floor


def pos_at_time(elev: Elevator, elev_call_list: List[dict], time: float) -> int:
    if len(elev_call_list) == 0:
        return 0
    if len(elev_call_list) == 1 and time > elev_call_list[0].get("call").time + time_floor2floor(elev, 0, elev_call_list[0].get("floor")):
        return elev_call_list[0].get("floor")
    total_time = elev_call_list[0].get("call").time + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))  # start elevator at time first call comes in + time to travel from 0 to first src
    for i in range(len(elev_call_list) - 1):
        if time <= total_time + time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor")):  # found range
            return pos_in_range(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"), time, total_time)  # step back in total_time
        if (total_time < elev_call_list[i+1].get("call").time) and (time <= elev_call_list[i+1].get("call").time):  # if there is a gap in the call_bank because of timing and once added the gap, now found range
            return elev_call_list[i].get("floor")
        if total_time < elev_call_list[i+1].get("call").time:  # added gap and still haven't found range
            total_time = elev_call_list[i+1].get("call").time  # update total_time
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i+1].get("floor"))
    return elev_call_list[-1].get("floor")


def fastest_elev(building: Building, call: CallForElevator, calls_bank: dict) -> (int, float):
    ans = 0
    temp_elev_call_list = []
    for floor in calls_bank[building.elevators[0].id]:
        temp_elev_call_list.append(floor)
    add_call_to_elevator_bank(call, building.elevators[0], temp_elev_call_list)
    min_time = time_to_complete_call(call, temp_elev_call_list, building.elevators[0])
    for elev in building.elevators[1:]:
        temp_elev_call_list = []
        for floor in calls_bank[elev.id]:
            temp_elev_call_list.append(floor)
        add_call_to_elevator_bank(call, elev, temp_elev_call_list)
        time = time_to_complete_call(call, temp_elev_call_list, elev)
        if time < min_time:
            min_time = time
            ans = elev.id
    return ans, min_time


def time_to_complete_call(call: CallForElevator, elev_call_list: List[dict], elev: Elevator) -> float:
    time = 0
    i = future_call_list(elev, elev_call_list, call.time)
    if i != -1:
        if pos_at_time(elev, elev_call_list, call.time) != elev_call_list[i].get("floor"):
            time += ceil(abs(pos_at_time(elev, elev_call_list, call.time) - elev_call_list[i].get("floor")) / elev.speed) + elev.stop_time + elev.open_time
        while i < len(elev_call_list)-1:
            if elev_call_list[i].get("call") == call and elev_call_list[i].get("floor") == call.dest:
                return time
            time += elev.close_time + elev.start_time + ceil(abs(elev_call_list[i].get("floor") - elev_call_list[i+1].get("floor")) / elev.speed) + elev.stop_time + elev.open_time
            i += 1
    return time


def add_call_to_elevator_bank(call: CallForElevator, elev: Elevator, elev_call_list: List[dict]) -> None:  # adds call src and dest to the elevators call list
    index = future_call_list(elev, elev_call_list, call.time)
    src_index = add_floor(call.src, elev_call_list, index, call.time, elev, call)
    add_floor(call.dest, elev_call_list, src_index, call.time, elev, call)


# take care of case where the floor is equal to a floor in the list
def add_floor(floor: int, elev_call_list: List[dict], index: int, time: float, elev: Elevator, call: CallForElevator) -> int:  # adds floor to the elevators call list
    if index == -1:
        elev_call_list.append({"floor": floor, "call": call})
        return 0
    elif index == 0:
        direction = "UP" if 0 < elev_call_list[index].get("floor") else "DOWN"
    else:
        direction = "UP" if elev_call_list[index-1].get("floor") < elev_call_list[index].get("floor") else "DOWN"
    pos = pos_at_time(elev, elev_call_list, time)
    if direction == "UP" and pos < floor < elev_call_list[index].get("floor"):
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    if direction == "DOWN" and pos > floor > elev_call_list[index].get("floor"):
        elev_call_list.insert(index, {"floor": floor, "call": call})
        return index
    for i in range(index, len(elev_call_list) - 1):
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


def future_call_list(elev: Elevator, elev_call_list: List[dict], time: float) -> int:
    if len(elev_call_list) == 0:
        return -1
    # returns an index pointing to what part of
    # the call_list the elevator got to at a certain time
    query_time = time
    # start elevator at time first call comes in + time to travel from 0 to first src
    total_time = elev_call_list[0].get("call").time + time_floor2floor(elev, 0, elev_call_list[0].get("floor"))
    for i in range(len(elev_call_list) - 1):
        if query_time <= total_time + time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i + 1].get("floor")):  # found index of curr list
            return i
        if (total_time < elev_call_list[i].get("call").time) and time <= elev_call_list[i + 1].get("call").time:  # if there is a gap in the call_bank because of timing and once added the gap, then found index
            return i
        if total_time < elev_call_list[i].get("call").time: # there is gap but have not yet found index
            total_time = elev_call_list[i].get("call").time # update
        total_time += time_floor2floor(elev, elev_call_list[i].get("floor"), elev_call_list[i + 1].get("floor"))
    return len(elev_call_list) - 1


if __name__ == '__main__':
    import doctest

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

    # for call in call_list:
    #     call.allocated_to = 0

    elevator_calls_bank = {}
    elevator_floor_calls_bank = {}
    for i in building.elevators:
        elevator_calls_bank[i.id] = []
        elevator_floor_calls_bank[i.id] = []

    for call in calls_list:
        fastest_id, fastest_time = fastest_elev(building, call, elevator_floor_calls_bank)
        ans = fastest_id
        call.allocated_to = ans
        elevator_calls_bank[ans].append(call)
        add_call_to_elevator_bank(call, building.elevators[ans], elevator_floor_calls_bank[ans])

    # write updated calls to a new file
    with open("test.csv", "w") as c:
        writer = csv.writer(c)
        for call in calls_list:
            writer.writerow(call.call_as_list())

    # c1 = CallForElevator(["", 15.74901825, 0, -6, 0, 0])
    # c2 = CallForElevator(["", 29.79572499, -4, 80, 0, 0])
    # c3 = CallForElevator(["", 30.19242759, -7, 88, 0, 0])
    # c4 = CallForElevator(["", 30.71595022, -5, 74, 0, 0])
    # call_list = [c1, c2, c3, c4]
    # elv = Elevator({
    #     "_id": 0,
    #     "_speed": 0.5,
    #     "_minFloor": -2,
    #     "_maxFloor": 10,
    #     "_closeTime": 2.0,
    #     "_openTime": 2.0,
    #     "_startTime": 3.0,
    #     "_stopTime": 3.0
    # })
    # call_bank = {elv.id, call_list}
    # e = Elevator({
    #     "_id": 0,
    #     "_speed": 2.0,
    #     "_minFloor": -2,
    #     "_maxFloor": 10,
    #     "_closeTime": 2.0,
    #     "_openTime": 2.0,
    #     "_startTime": 3.0,
    #     "_stopTime": 3.0
    # })
    # print(assign_to_elevator(e, c))

