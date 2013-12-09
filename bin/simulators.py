"""
simulators.py

Parse read files generated by simulators and annotate them with information
about their point/configuration of origin.

Better if we can do everything we need just given the read name.
"""

import re

def sameAlignment(al, left, refid, fw, wiggle=10):
    alpos = al.pos - al.softClippedLeft()
    return refid == al.refid and \
           abs(left - alpos) < wiggle and \
           al.fw == fw, abs(left - alpos)

_wgsimex_re = re.compile('(.+)_([^_]+)_([^_]+)_([^:]+):([^:]+):([^_]+)_([^:]+):([^:]+):([^_]+)_([^_]+)_([^_]+)_([^_]+)_([^/]+).*')
#                           1   2       3       4       5       6       7       8       9       10      11      12      13

def isExtendedWgsim(nm):
    ret = _wgsimex_re.match(nm) is not None
    return ret

def parseExtendedWgsim(al):
    ''' Note: this is my extended version of wgsim's output '''
    nm = al.name
    res = _wgsimex_re.match(nm)
    refid, fragst1, fragen1 = res.group(1), int(res.group(2))-1, int(res.group(3))-1
    len1, len2 = int(res.group(10)), int(res.group(11))
    flip = res.group(12) == '1'
    mate1 = al.mate1 or not al.paired
    ln = len1 if mate1 else len2
    if (not flip) == mate1:
        return fragst1, refid, True
    else:
        return fragen1 - (ln-1), refid, False

def correctExtendedWgsim(al, wiggle=10):
    st, refid, fw = parseExtendedWgsim(al)
    return sameAlignment(al, st, refid, fw, wiggle=wiggle)

def parseSimulatedReadName(nm):
    return parseExtendedWgsim(nm)
