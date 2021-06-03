#!/usr/bin/env python3
import re

ORIGINS = {
        'db.cslabs': 'cslabs.clarkson.edu',
        'db.cosi': 'cosi.clarkson.edu',
        #'db.csprojects': 'csprojects.clarkson.edu',
}

REVERSE = {
        #'db.cslabs.rvs': ?,
        'db.cslabs.rvs.144': '128.153.144.',
        'db.cslabs.rvs.145': '128.153.145.',
        'db.cslabs.rvs.146': '128.153.146.',
        'db.cslabs.rvs.c051': '2605:6480:c051:',
}

RECPAT = re.compile(r'''
        ^\s*
        (?P<name>[a-zA-Z0-9_\.-]+)
        (?:\s+
        (?P<class>[a-zA-Z]+))?
        \s+
        (?P<type>[a-zA-Z]+)
        \s+
        (?P<value>.*$)
''', re.X)

class Record(object):
    __slots__ = ['name', 'cls', 'tp', 'value']

    def __init__(self, name, cls, tp, value):
        self.name = name
        self.cls = cls
        self.tp = tp
        self.value = value

    @classmethod
    def from_match(cls, match):
        return cls(
                *match.group('name', 'class', 'type', 'value')
        )

    def __repr__(self):
        return f'Record(name={self.name!r}, cls={self.cls!r}, tp={self.tp!r}, value={self.value!r})'

    def __hash__(self):
        return hash((self.name, self.cls, self.tp, self.value))

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return (self.name, self.cls, self.tp, self.value) == (other.name, other.cls, other.tp, other.value)

FWD = {}  # zonefile -> [record]
RVS = {}  # id

def get_recs_from_file(f):
    rv = []
    for line in open(fn):
        match = RECPAT.match(line)
        if not match:
            print(f'rejected line: {line!r}')
            continue
        rec = Record.from_match(match)
        rv.append(rec)
    return rv

def expand_ip6(s):
    groups = s.split(':')
    zs = 8 - len(list(filter(None, groups)))
    if zs > 0:
        fi = groups.index('')
        groups = groups[:fi] + ['0000'] * zs + groups[fi+1:]
    return ':'.join(i.rjust(4, '0') for i in groups)

def into_digits(addr):
    return [c for c in addr if c != ':']

def canon_ip6(digits):
    groups = [''.join(digits[i*4:(i+1)*4]) for i in range(8)]
    fz, lz = None, None
    try:
        fz = groups.index('0000')
    except ValueError:
        pass
    else:
        lz = len(groups) - list(reversed(groups)).index('0000')
    groups = [i.lstrip('0') for i in groups]
    if fz is not None:
        return ':'.join(groups[:fz]) + '::' + ':'.join(groups[lz:])
    return ':'.join(groups)

def cons_addr(rec, org):
    if rec.tp != 'PTR':
        raise ValueError(rec)
    if '.' in org:
        parts = '.'.join(reversed(rec.name.split('.')))
        return org + parts
    elif ':' in org:
        digits = list(reversed(rec.name.split('.')))
        digits = [i for i in org if i != ':'] + digits
        return canon_ip6(digits)


for fn, zone in ORIGINS.items():
    FWD[fn] = get_recs_from_file(open(fn))

for fn, rv in REVERSE.items():
    RVS[fn] = get_recs_from_file(open(fn))

for za in ORIGINS.keys():
    for zb in ORIGINS.keys():
        if za <= zb:
            continue
        print('Comparison between', za, 'and', zb)
        sa = set(FWD[za])
        sb = set(FWD[zb])
        ma = sb - sa
        mb = sa - sb
        print(f'Missing from {za}:')
        for i in ma:
            print('\t', i)
        print(f'Missing from {zb}:')
        for i in mb:
            print('\t', i)

mrvs = {}  # canonaddr -> rec
seen_addrs = {} # addr -> oldname
seen_names = {} # name -> firstaddr
for z in ORIGINS.keys():
    for rec in FWD[z]:
        if rec.tp == 'A':
            mrvs[rec.value] = rec
        elif rec.tp == 'AAAA':
            mrvs[canon_ip6(into_digits(expand_ip6(rec.value)))] = rec
print('Reverse records:')
for r, addr in REVERSE.items():
    for rec in RVS[r]:
        if rec.tp != 'PTR':
            continue
        a = cons_addr(rec, addr)
        if a in seen_addrs:
            print(f'\t- Rvs {a} (for {rec.value}) has already been seen as {seen_addrs[a]}')
        else:
            try:
                del mrvs[a]
            except KeyError:
                print(f'\t- Rvs {a} (supposedly {rec.value}) doesn\'t correspond to any forward record')
            seen_addrs[a] = rec.value
        if rec.value in seen_names:
            print(f'\t- Name {rec.value} (for {a}) has already been seen as {seen_names[rec.value]}')
        else:
            seen_names[rec.value] = a

for addr, rec in mrvs.items():
    print(f'\t- No rvs for {addr} (in {rec!r})')

#for fn, recs in FWD.items():
#    for rec in recs:
#        print(fn, ':', rec)
#        if rec.tp == 'AAAA':
#            print(canon_ip6(into_digits(expand_ip6(rec.value))))
#for fn, recs in RVS.items():
#    for rec in recs:
#        print(fn, ':', rec)
#        if rec.tp == 'PTR':
#            print(cons_addr(rec, REVERSE[fn]))
