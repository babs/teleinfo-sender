#!/usr/bin/python
import sys, serial, datetime, time, threading, urllib2, json
from Colorize import colorize
from Queue import Queue



class glob:
    workthread = None
    destination = []
    trames = Queue()
    counter = 0L
    counterlock = threading.Lock()
    wrap_at = 60

def checksum(line):
    return chr((
        sum(
            map(
                lambda x: ord(x),
                 " ".join(line.split(" ")[:2]))
            ) & 0x3F)
         + 0x20)

def push_data(trame):
    exc = {}
    for dest in glob.destination:
        try:
            urllib2.urlopen(urllib2.Request(
                dest,
                json.dumps(trame),
                {'Content-Type':'application/json'})).read()
        except Exception, e:
            exc[dest] = e
    if len(exc) > 0:
        raise Exception("Push failed!", exc)

def write_progress(c):
    with glob.counterlock:
        glob.counter = glob.counter + 1
        sys.stdout.write(c)
        if glob.counter % glob.wrap_at == 0:
            sys.stdout.write("\n")
        sys.stdout.flush()

def worker():
    while True:
        item = glob.trames.get()
        try:
            push_data(item)
            write_progress("+")
        except:
            # failed, put back
            glob.trames.put(item)
            write_progress("-")
            time.sleep(2)
        glob.trames.task_done()

def main():
    if len(sys.argv) > 1:
        glob.destination = sys.argv[1:]
    else:
        print colorize("no destination set!", fg="red", bold=True)
        sys.exit(1)

    print colorize("Starting worker", fg="green", bold=True)
    print colorize("[*] sending to %s"%str(glob.destination), fg="green")
    glob.workthread = threading.Thread(target=worker)
    glob.workthread.daemon = True
    glob.workthread.start()

    print colorize("Starting collection", fg="green", bold=True)
    ser = serial.Serial("/dev/ttyUSB0", 1200)
    buf = []
    trame = []
    tramets = None
    laststart = None
    while True:
        c = ser.read()
        if c == "\x02": # Debut de trame
            tramets = time.time()
            trame = [c]
            duration = ""
            if laststart != None:
                duration = str(datetime.datetime.now()-laststart)
            #laststart = datetime.datetime.now()
            #print "***start %s"%colorize(duration, bold=True)
            continue
        if c == "\x03": # fin de trame
            #print "***end"
            trame.append(c)
            if tramets != None:
                glob.trames.put({"tramets": tramets, "trame":  "".join(trame)})
                write_progress(".")
            continue
        if c == "\x0a": # Debut de ligne
            buf = []
            continue
        if c == "\x0d": # Fin de ligne
            line = "".join(buf)
            trame.append("\x0a" + line + "\x0d")
        buf.append(c)

if __name__ == "__main__":
    main()

