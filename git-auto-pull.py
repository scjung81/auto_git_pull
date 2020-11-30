#!/usr/bin/env python
# 상위 디렉토리를 돌면선 git pull 진행
# 결과는 mail 로 전달

import os
import subprocess
import argparse
from pathlib import Path

import datetime
import sys
from sendMail import *

dayOfWeek = ['월', '화', '수', '목', '금', '토', '일']
def getCurrentDate(t=3):
    dt = datetime.datetime.now()
    if t == 1:
        return dt.strftime("%A %d. %B %Y %H:%M:%S")
    elif t == 2:
        return dt.strftime("%Y%m%d") + "(" + dayOfWeek[dt.weekday()] + ")"
    elif t == 3:
        return dt.strftime("%Y%m%d")
    elif t == 4:
        return dt.strftime("%m%d")
    elif t == 5:
        return dt.strftime("%Y%m%d") + "_" + dayOfWeek[dt.weekday()] + "_" + dt.strftime("%H%M%S")
    elif t == 6:
        return dt.strftime("%Y%m%d") + "_" + dayOfWeek[dt.weekday()] + "_" + dt.strftime("%H:%M:%S")

log_dir = Path().resolve().as_posix()+"/log"
log_path = log_dir + f"/log_{getCurrentDate()}.txt"
def write_log(str, wai=sys.argv[0]):
    if str == "":
        return
    os.makedirs(log_dir, exist_ok=True)

    if str.endswith("\n"):
        str = str[:-1]

    log = f"[{getCurrentDate(t=6)}][{'/'.join(wai.split('/')[-2::1])}][{os.getpid()}]: {str}\n"

    print(log)
    sys.stdout.flush()

    with open(log_path, "a", encoding='utf8') as file:
        file.write(log)
        file.close()

def parse_args():
    parser = argparse.ArgumentParser(description= \
            "Pulling for all of git-repositories from a specific directory recursively")

    parser.add_argument("-b", "--branch", required=False, type=str, help="Branch name to pull")
    parser.add_argument("-p", "--path", type=str, help="Path you want to start pulling")

    args = parser.parse_args()
    return args

def is_git_repo(path):
    return subprocess.call(['git', '-C', path, 'status'], \
            stderr=subprocess.STDOUT, stdout=open(os.devnull, 'w')) == 0

def exec_pull(branch):
    # checkout_cmd = "git checkout " + branch
    print("git pull")
    # subprocess.call(checkout_cmd, shell=True)
    result = subprocess.check_output("git pull", shell=True, stderr=subprocess.STDOUT,  universal_newlines=True)
    write_log(result)

def run(path, branch):
    filenames = os.listdir(path)
    pathlist = [ os.path.join(path, filename) for filename in filenames ]
    dirlist = [ path for path in pathlist if os.path.isdir(path) ]
    i = 1
    for path in dirlist:
        if is_git_repo(path):
            write_log(f"===========[ {i} ]===========")
            old_path = os.getcwd()
            os.chdir(path)
            write_log(path + " is git repo")
            result = subprocess.check_output("git diff", shell=True, universal_newlines=True ) #, encoding='utf-8')
            write_log(result)

            exec_pull(branch)

            os.chdir(old_path)
        # else:
        #     run(path, branch)

            i += 1

def main():
    args = parse_args()

    branch = args.branch
    start_path = Path().resolve().parent

    print(f"start_path = {start_path}")

    if args.path != None:
        start_path = args.path

    run(start_path, branch)

    files = []
    files.append(log_path)

    title = "Git pull Complete"
    with open(log_path, "r" , encoding='utf8') as file:
        text = file.read()

    sendMail(to=['neo2544@naver.com'], text=text , title=title, files=files)

if __name__ == "__main__":
    main()

