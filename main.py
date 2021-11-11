import sys
import csv
import json


class Building:
    def __init__(self, elevs, minFloor, maxFloor):
        self.elevators = elevs
        self.minFloor = minFloor
        self.maxFloor = maxFloor


class Elevator:
    def __init__(self, d):
        self.id = d.get("_id")
        self.speed = d.get("_speed")
        self.minFloor = d.get("_minFloor")
        self.maxFloor = d.get("_maxFloor")
        self.closeTime = d.get("_closeTime")
        self.openTime = d.get("_openTime")
        self.startTime = d.get("_startTime")
        self.stopTime = d.get("_stopTime")
        self.pos = 0

    def __str__(self):
        return str({"_id": self.id, "_speed": + self.speed, "_minFloor": self.minFloor, "_maxFloor": self.maxFloor, "_closeTime": self.closeTime, "_openTime": self.openTime, "_startTime": self.startTime, "_stopTime": self.stopTime})


class Call:
    def __init__(self, l):
        self.time = float(l[1])
        self.src = int(l[2])
        self.dest = int(l[3])
        self.allocatedTo = int(l[5])

    def time_to_complete_call(self, elev: int) -> float:
        time = 0
        return time


    def call_array(self) -> list:
        return ["Elevator call", self.time, self.src, self.dest, 0, self.allocatedTo]

    def __str__(self) -> str:
        return str(["Elevator call", self.time, self.src, self.dest, 0, self.allocatedTo])


if __name__ == '__main__':
    # elevlist = []
    # building from json
    with open(sys.argv[1], "r") as j:  # in order to take all of the elevators from the json
        reader = json.load(j)
        minFloor = reader.get("_minFloor")
        maxFloor = reader.get("_maxFloor")
        elevs = reader.get("_elevators")
        # for elev in elevs:
        #     e = Elevator(elev)
        #     elevlist.append(e)
        elevlist = [Elevator(elev) for elev in elevs]
    building = Building(elevlist, minFloor, maxFloor)

    # calls from csv
    # calllist = []
    with open(sys.argv[2], "r") as c:  # in order to take all of the elevator calls from csv
        reader = csv.reader(c)
        # for line in reader:
        #     c = Call(line)
        #     calllist.append(c)
        calllist = [Call(line) for line in reader]

    for call in calllist:
        call.allocatedTo = 0

    with open("test.csv", "w") as c:
        writer = csv.writer(c, dialect='excel')
        # writer.writerow(calllist)
        for call in calllist:
            writer.writerow(call.call_array())
