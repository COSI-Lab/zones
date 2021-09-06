#!/usr/bin/env python3
import re, sys, os

prop_serial = None
if len(sys.argv) > 1:
    try:
        prop_serial = int(sys.argv[1])
    except ValueError:
        print(f'Usage: {sys.argv[0]} <serialnum>')
        exit(1)

FILES = [
    'db.cosi',
    'db.cslabs',
    'db.csprojects',
    #'db.cslabs.rvs',
    'db.cslabs.rvs.144',
    'db.cslabs.rvs.145',
    'db.cslabs.rvs.146',
    'db.cslabs.rvs.c051',
]

SERPAT = re.compile(r'(\d+)(\s*;\s*serial)')

maxser = None
data = {}
for fname in FILES:
    content = open(fname).read()
    data[fname] = content
    match = SERPAT.search(content)
    if not match:
        print(f'Could not find pattern in file {fname}; abort.')
        exit(1)
    ser = int(match.group(1))
    print(f'Ser for {fname}: {ser}')
    if maxser is None:
        maxser = ser
    else:
        maxser = max((maxser, ser))

print(f'Detected maximum serial: {maxser}')

if prop_serial is None:
    prop_serial = maxser + 1
elif prop_serial <= maxser:
    print(f'Warning: proposed serial {prop_serial} <= {maxser}')

while True:
    resp = input(f'Proposing serial {prop_serial}; update [y/n]? ')
    if resp.lower() == 'y':
        print('Ok, editing...')
        break
    elif resp.lower() == 'n':
        print('Abort.')
        exit(1)
    else:
        print('Please enter "y" or "n".')

for fname in FILES:
    bakname = fname + '.bak'
    print(f'Writing backup of {fname} to {bakname}...')
    open(bakname, 'w').write(data[fname])

for fname in FILES:
    print(f'Writing {fname}...')
    open(fname, 'w').write(SERPAT.sub(f'{prop_serial}\\2', data[fname]))

print('Done.')
