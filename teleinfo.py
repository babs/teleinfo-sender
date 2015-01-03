#!/usr/bin/python

import sys, serial, datetime
from Colorize import colorize

def checksum(line):
    return chr((sum(map(lambda x: ord(x), " ".join(line.split(" ")[:2]))) & 0x3F) + 0x20)

def main():
    print colorize("starting", fg="red")
    ser = serial.Serial("/dev/ttyUSB0", 1200)
    buf = []
    laststart = None
    while True:
        c = ser.read()
        if c == "\x02":
            duration = ""
            if laststart != None:
                duration = str(datetime.datetime.now()-laststart)
            laststart = datetime.datetime.now()
            print "***start %s"%colorize(duration, bold=True)
            continue
        if c == "\x03":
            print "***end"
            continue
        if c == "\x0a": # Debut de ligne
            buf = []
            continue
        if c == "\x0d": # Fin de ligne
            line = "".join(buf)
            if not checksum(line) == line[-1]: bg="red"
            bold = bg = fg = None
            if "PAPP" in line:
                fg="red"
                bold=True
            if "ADCO" in line:
                fg="green"
                bold=True
            sys.stdout.write(colorize(line, fg=fg, bg=bg,bglight=False, fglight=True, bold=bold)+"\n")
            continue
        buf.append(c)
if __name__ == "__main__":
    main()

