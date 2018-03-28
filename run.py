#!/bin/env python3

import csv
import subprocess
import io
import tabulate

def parse_csv_line(ln):
    flags = {   'NORSA,':       'Good',
                'SAFE,' :       'Good',
                'VULNERABLE,':  '**Bad**',
                'NOTLS,':       'Error',
                'NODNS,':       'Error',
                'INCONSISTENT,':'Unsure',
            }
    for key,verdict in flags.items():
        if ln.startswith(key):
            flag, host, ip = ln.split(',')[:3]
            return flag, host, ip, verdict

headers = ['Name', 'Host', 'Port', 'IP', 'Flag', 'Verdict']
all_results = []
with open('banks.csv') as f:
    subprocess.run('date', shell=True)

    for row in csv.reader(f):
        host, port, name = row

        cmd = './robot-detect --csv -p {port} {host}'.format(host=host, port=port)
        print('============== {} ==========='.format(name))
        print('calling: {}'.format(cmd))
        res = subprocess.run(cmd, shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )
        print('retcode: {}'.format(res.returncode))

        flag, ip, verdict = 'HUH?', '0.0.0.0', 'Error'
        for ln in io.TextIOWrapper(io.BytesIO(res.stdout)):
            pln = parse_csv_line(ln)
            if pln is None:
                print(ln)
            else:
                flag, _, ip, verdict = pln
        all_results.append( (name,host,port,ip,flag,verdict) )

with open('README.md', 'w') as fout:
    fout.write('''
# ROBOT Hall of Shame

A summary showing whether a bank's online-banking site is vulnerable to [ROBOT](https://robotattack.org).

To those banks marked *bad*, shame on you!

''')
    fout.write(tabulate.tabulate(all_results, headers, tablefmt='pipe'))

    fout.write('''

This file is generated authomatically with `run.py`, which in turn calls the
detection code from [this repo](https://github.com/robotattackorg/robot-detect/).

Currently I only included in `banks.csv` a dozon of banks that I know, mostly in Asia.
If you know more banks, PRs welcome.

''')

