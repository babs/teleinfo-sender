#!/usr/bin/env python
import  sys

USE_COLOR=0
if sys.stdout.isatty():
    USE_COLOR=1

DEFAULT_LIGHT=True

import logging
class ColHandler(logging.StreamHandler):
    def emit(self, record):
        fgc  = None
        bold = None
        bgc  = None
        if record.levelno < 20:
            fgc = "blue"
        elif record.levelno < 30:
            fgc = "green"
        elif record.levelno < 40:
            fgc = "yellow"
        else:
            fgc = "red"
        # print dir(self.stream)
        self.stream.write( colorize(self.format(record), fg=fgc, bg=bgc, bold=bold)+"\n")

def init_root_logger(format="%(asctime)s %(name)-15s %(levelname)-8s %(message)s", level=1):
    log = logging.getLogger()
    formatter = logging.Formatter(format)
    sh = ColHandler()
    sh.setFormatter(formatter)
    log.setLevel(level)
    log.addHandler(sh)
    return log

def colorize(txt, fgcol=None, bgcol=None, bold=None, underline=None, blink=None, reverse=None, stroke=None, dark=None, light=True, fglight=None, bglight=None, **kwarg):
    " => colorize(text, foreground color, background color, bold, underline, blink, reverse, stroke, light, background light, foreground light) returns text with escapes codes\npossible colors are black, red, green, yellow, blue, pink, cyan and white."
    cols = {
        'black':0,
        'red':1,
        'green':2,
        'yellow':3,
        'blue':4,
        'pink':5,
        'cyan':6,
        'white':7
        }
    if not USE_COLOR: return txt
    if kwarg.has_key('fg'): fgcol = kwarg['fg']
    if kwarg.has_key('bg'): bgcol = kwarg['bg']
    if kwarg.has_key('bold'): bold = kwarg['bold']
    if kwarg.has_key('underline'): underline = kwarg['underline']
    if kwarg.has_key('blink'): blink = kwarg['blink']
    if kwarg.has_key('reverse'): reverse = kwarg['reverse']
    if kwarg.has_key('stroke'): stroke = kwarg['stroke']
    if kwarg.has_key('dark'): dark = kwarg['dark']
    if kwarg.has_key('light'): light = kwarg['light']
    if kwarg.has_key('fglight'): fglight = kwarg['fglight']
    if kwarg.has_key('bglight'): bglight = kwarg['bglight']
    if fgcol and not fgcol in cols.keys():
        return txt
    if bgcol and not bgcol in cols.keys():
        return txt
    if light and not dark: fglight = 1
    codes = []
    lbold = ""
    if underline:
        codes.append("4")
        
    if blink:
        codes.append("5")

    if reverse:
        codes.append("7")

    if bold:
        codes.append("1")
        lbold= "1;"
    if stroke:
        codes.append("9")
    if dark:
        codes.append("2")
    if fgcol:
        int_char = "3"
        if fglight: int_char="9"
        codes.append(int_char+str(cols[fgcol]))
    if bgcol:
        int_char = "4"
        if bglight: int_char="10"
        codes.append(int_char+str(cols[bgcol]))
    startcode = '\033['
    endcode  = '\033[0m'
    return startcode + ";".join(codes) + 'm' + txt + endcode


def splitCol(col):
    if col[0] == "#":
        col = col[1:]
    return [ int(col[0:2],16), int(col[2:4],16), int(col[4:6],16)]
    
def buildColScale(scol, ecol, steps, prepend="#"):
    start = splitCol(scol)
    if steps < 2:
        return [prepend+"%.2x%.2x%.2x"%(start[0],start[1],start[2])]
    end = splitCol(ecol)
    step = [ float(end[0]-start[0])/(steps-1), float(end[1]-start[1])/(steps-1), float(end[2]-start[2])/(steps-1) ]
    retlist = []
    for i in range(0,steps):
        s = prepend
        s += "%.2x%.2x%.2x"%(start[0]+(step[0]*i),start[1]+(step[1]*i),start[2]+(step[2]*i),)
        retlist.append(s)
    return retlist

def RGBtoHSV(*args):
    if len(args) == 1:
        (r,g,b) = splitCol(args[0])
    elif len(args) == 3:
        (r,g,b) = args
    # print "Red   : %d\tGreen : %d\tBlue  : %d"%(r,g,b)
    (r,g,b) = map(lambda x: x/255.0,(r,g,b))
    # print "Red   : %f\tGreen : %f\tBlue  : %f"%(r,g,b)
    var_Max = max(r,g,b)
    var_Min = min(r,g,b)
    delta   = var_Max - var_Min
    v = var_Max
    if delta == 0:
        h = 0.0
        s = 0.0
    else:
        s = delta/var_Max
        delta_r = ( ( ( var_Max - r ) / 6.0 ) + ( delta / 2.0 ) ) / delta
        delta_g = ( ( ( var_Max - g ) / 6.0 ) + ( delta / 2.0 ) ) / delta
        delta_b = ( ( ( var_Max - b ) / 6.0 ) + ( delta / 2.0 ) ) / delta
        if r == var_Max:
            h = delta_b - delta_g
        elif g == var_Max:
            h = ( 1.0 / 3.0 ) + delta_r - delta_b
        elif b == var_Max:
            h = ( 2.0 / 3.0 ) + delta_g - delta_r
        if h < 0:
            h = h + 1
        if h > 1:
            h = h -1
    return [h*360,s*100,v*100]
    
def HSVtoRGB(*args):
    if len(args) == 3:
        h = args[0]
        s = args[1]
        v = args[2]
    elif len(args) == 1:
        (h,s,v) = args[0]
    h = h%360
    h = h/360.0
    s = s/100.0
    v = v/100.0
    if s == 0:
        r = g = b = v
    else:
        h = h * 6.0
        if h == 6.0:
            h = 0
        i = int(h)
        t1 = v * ( 1 - s )
        t2 = v * ( 1 - s * ( h - i ) )
        t3 = v * ( 1 - s * ( 1 - ( h - i ) ) )
        if i == 0:
            r = v
            g = t3
            b = t1
        elif i == 1:
            r = t2
            g = v
            b = t1
        elif i == 2:
            r = t1
            g = v
            b = t3
        elif i == 3:
            r = t1
            g = t2
            b = v
        elif i == 4:
            r = t3
            g = t1
            b = v
        else:
            r = v
            g = t1
            b = t2
    return map(lambda x: x*255, [r,g,b])

