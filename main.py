import sys
import csv
import json


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
        self.waiting_time = (self.dest - self.src) > 0

    def time_to_complete_call(self, elev: Elevator) -> float:
        return 1 - (self.time - int(self.time)) + 1 + elev.start_time + ((abs(self.src - self.dest) - 1) / elev.speed) + elev.stop_time + elev.open_time + elev.close_time

    def call_as_list(self) -> list:
        return ["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to]

    def __str__(self) -> str:
        return str(["Elevator call", self.time, self.src, self.dest, 0, self.allocated_to])


def time_floor2floor(elev: Elevator, a: int, b: int) -> float:
    return elev.close_time + elev.start_time + (abs(a-b)/elev.speed) + elev.stop_time + elev.open_time


def pos_in_range(elev: Elevator, going_from: int, going_to: int, q_time: float, t_time: float) -> int:
    floor = going_from
    # first add close_time and see if that makes a difference
    t_time += elev.close_time
    if t_time > q_time:
        return floor
    t_time += elev.start_time
    # elevator already started so now can only stop at next floor up or down depending on direction
    if t_time > q_time and (going_from < going_to):  # elevator is going up
        return floor + 1
    if t_time > q_time and (going_from > going_to):  # elevator is going down
        return floor -1
    # now going through in-between floors
    for fl in range(abs(going_from - going_to)):
        if going_from < going_to:  # elevator is going up
            t_time += (1/elev.speed)
            floor = floor + 1  # 'pos' increases by one
        if going_from > going_to:  # elevator is going down
            t_time += (1 / elev.speed)
            floor = floor - 1  # 'pos' decreases by one
        if t_time >= q_time:
            return floor


def pos_at_time(elev: Elevator, call_list: list, time: float) -> int:  # FINISH THIS
    query_time = time
    # start elevator at time first call comes in + time to travel from 0 to first src
    total_time = calls_list[0].get("call").time + time_floor2floor(elev, 0, call_list[0].get("floor"))
    for i in range(len(call_list)-1):
        # if there is a gap in the call_list because of timing
        if total_time < call_list[i].get("call").time:
            total_time += (call_list[i].get("call").time - total_time)
        total_time = total_time + time_floor2floor(elev, call_list[i].get("floor"), call_list[i+1].get("floor"))
        if query_time <= total_time:  # found range
            return pos_in_range(elev, call_list[i].get("floor"), call_list[i+1].get("floor"), query_time, (total_time - (time_floor2floor(elev, call_list[i].get("floor"), call_list[i+1].get("floor")))))  # step back in total_time


def assign_to_elevator(building: Building, call: CallForElevator):  # FINISH THIS
    ans = 0
    for elev in building.elevators:
        call.waiting_time = call.time_to_complete_call(elev)
    return call.waiting_time


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

    # for call in call_list:
    #     call.allocated_to = 0

    elevator_calls = {}
    elevator_floor_calls = {}
    for i in building.elevators:
        elevator_calls[i.id] = []
        elevator_floor_calls[i.id] = []

    # for call in calls_list:
    #     assign_to_elevator(call)

    with open("test.csv", "w") as c:
        writer = csv.writer(c)
        # writer.writerow(calllist)
        for call in calls_list:
            writer.writerow(call.call_as_list())

    # c = Call_For_Elevator(["", 88, 10, 0, 0, 1])
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
