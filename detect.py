
import json
from subprocess import Popen, PIPE
from argparse import ArgumentParser


def gen_stat(txt: dict):
    for k in txt.keys():
        yield (k, len(txt[k]))


def stat(fname: str):
    try:
        with open(fname, 'r') as f:
            return gen_stat(json.loads(f.read()))
    except OSError as er:
        raise SystemExit(er)


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
    group.add_argument('-v', action='store_true', help='версия программы')
    group.add_argument('-h', action='help', help='справка о работе программы')
    group.add_argument('-p', nargs='?', type=str, action='store', metavar='', help='имя пакета')
    group.add_argument('-stat', nargs='?', type=str, action='store', metavar='', help='файла')

    opt = parser.add_argument_group()
    opt.add_argument('-f', dest='file_save', nargs='?', type=str, help='сохранить в файл с заданным именем', metavar='')
    opt.add_argument('-s', dest='file_same', action='store_true', help='сохранить в файл с именем {rpm}.json')

    args = parser.parse_args()
    if args.v:
        print(VERSION)
    if args.p:
        if args.file_save:
            with open(args.file_save, 'w') as f:
                f.write(json.dumps(tree(args.p), indent=4, sort_keys=True))
        elif args.file_same:
            with open(f'{args.p}.json', 'w') as f:
                f.write(json.dumps(tree(args.p), indent=4, sort_keys=True))
        else:               
            print(json.dumps(tree(args.p), indent=4, sort_keys=True))
    if args.stat:
        print('statistics')
        [print(x) for x in stat(args.stat)]
    raise SystemExit()

