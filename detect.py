
import json
from subprocess import Popen, PIPE
from argparse import ArgumentParser


def gen(collection: list):
    for el in collection:
        el = el.strip()
        if not el:
            continue
        yield el


def exec(cmnd: str):
    proc = Popen(cmnd, shell=True, stdout=PIPE, stderr=PIPE)
    res, er = proc.communicate()
    return res.decode(), er


def check_file(res: dict, fname: str):
    line, _ = exec(f'ls -dZ {fname}')
    context, fname = list(gen(line.split()))
    res.update({context: [fname]}) if res.get(context) is None else res[context].append(fname)


def tree(rpmname: str) -> dict:
    rpm_files, _ = exec(f'rpm -ql {rpmname}')
    rpm_files = gen(rpm_files.split('\n'))
    res = {}
    [check_file(res, item) for item in rpm_files]
    return res


NAME = ''
DESCRIPTION = ''
VERSION = 0.1

if __name__ == '__main__':
    parser = ArgumentParser(prog=NAME, usage=DESCRIPTION, add_help=False, allow_abbrev=False)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-v', action='store_true', help='version')
    group.add_argument('-h', action='help', help='about')
    group.add_argument('-p', nargs='?', type=str, action='store', metavar='', help='package name')

    opt = parser.add_argument_group()
    opt.add_argument('-f', dest='file_save', nargs='?', type=str, help='save to file', metavar='')

    args = parser.parse_args()
    if args.v:
        print(VERSION)
    if args.p:
        if args.file_save:
            with open(args.file_save, 'w') as f:
                f.write(json.dumps(tree(args.p), indent=4, sort_keys=True))
        else:
            print(json.dumps(tree(args.p), indent=4, sort_keys=True))
    raise SystemExit()
