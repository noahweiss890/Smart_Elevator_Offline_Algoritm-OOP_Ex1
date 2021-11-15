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
    return elev.close_time + elev.start_time + (abs(a-b)/elev.speed) + elev.stop_time + elev.open_time


def pos_in_range(elev: Elevator, going_from: int, going_to: int, q_time: float, t_time: float) -> int:
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
            t_time += (1 / elev.speed)
            floor -= 1  # 'pos' decreases by one
        if t_time >= q_time:
            return floor


def pos_at_time(elev: Elevator, call_bank: dict, time: float) -> int:
    query_time = time
    total_time = call_bank[elev.id][0].get("call").time + time_floor2floor(elev, 0, call_bank[elev.id][0].get("floor"))  # start elevator at time first call comes in + time to travel from 0 to first src
    for i in range(len(call_bank[elev.id]) - 1):
        if total_time < call_bank[elev.id][i].get("call").time:  # if there is a gap in the call_bank because of timing
            total_time += (call_bank[elev.id][i].get("call").time - total_time)
        if query_time <= total_time + time_floor2floor(elev, call_bank[elev.id][i].get("floor"), call_bank[elev.id][i + 1].get("floor")):  # found range
            return pos_in_range(elev, call_bank[elev.id][i].get("floor"), call_bank[elev.id][i + 1].get("floor"), query_time, total_time)  # step back in total_time


def assign_to_elevator(building: Building, call: CallForElevator) -> None:  # FINISH THIS
    pass


def add_call_to_elevator_bank(call: CallForElevator, elev: Elevator, elev_call_list: List[dict]) -> None:  # adds call src and dest to the elevators call list
    index = future_call_list(elev_call_list, call.time)
    src_index = add_floor(call.src, elev_call_list, index)
    add_floor(call.dest, elev_call_list, src_index)


def add_floor(src: int, elev_call_list: List[dict], index: int) -> int:  # adds floor to the elevators call list
    direction = elev_call_list
    for i in range(index, len(elev_call_list) - 1):
        if elev_call_list[i] < elev_call_list[i+1]:
            pass
    return 0


def future_call_list(elev_call_list: List[dict], time: float) -> int:  # returns an index pointing to what part of the call_list the elevator got to at a certain time
    return 0


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

    # for call in calls_list:
    #     assign_to_elevator(call)

    with open("test.csv", "w") as c:
        writer = csv.writer(c)
        # writer.writerow(calllist)
        for call in calls_list:
            writer.writerow(call.call_as_list())

    # c = CallForElevator(["", 88, 10, 0, 0, 1])
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

