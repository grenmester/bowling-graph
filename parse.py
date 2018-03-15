#!/usr/bin/env python
import datetime

def removeExcessLines():
    access = "w"
    with open("new.md", "r") as source:
        lines = source.readlines()
        for line in lines:
            if line[0] == "#":
                date = line[2:-1]
                formattedDate = datetime.datetime.strptime(date, "%b %d, %Y")
                firstDay = datetime.datetime(year=2017, month=1, day=1)
                relDate = (formattedDate - firstDay).days + 1
            elif "* bowling" in line:
                start = line.find("(") + 1
                end = line.find(")")
                if start != 0:
                    scores = line[start:end].split(',')
                    scores = map(lambda x: int(x), scores)
                    with open("unparsed.md", access) as data:
                        access = "a"
                        avg = sum(scores) / len(scores)
                        data.write(str([relDate, avg, date, scores]) + "\n")

def convertToGraphableFormat():
    with open("unparsed.md", "r") as source:
        lines = source.readlines()
        arr = []
        for line in lines:
            line = eval(line)
            arr.append((line[0],line[1]))
        print(arr)

if __name__ == "__main__":
    removeExcessLines()
