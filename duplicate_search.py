#!/usr/bin/env python
# -*- coding: utf8 -*-

""" Search for duplicate files.

This script finds and removes duplicate files when comparing directories.
In this case, the first directory is considered the standard and the files in it remain unchanged.
This script can be used after recovering data by signatures.
"""

__author__ = 'Andrey Kravtsov'
__version__ = '1.0'

import hashlib
import pathlib
from datetime import datetime


def start_time():
    """Returns the current date and time"""
    now = datetime.now()
    return str(now.strftime("%d-%m-%Y %H:%M:%S"))


def folder_scan(path_: str, name_list: list, err_list: list) -> list:
    """Recursive directory traversal and returns a list of files"""
    try:
        for i in pathlib.Path(path_).glob('**/*'):
            if pathlib.Path(i).is_file():
                name_list.append(str(i))
        return name_list
    except PermissionError as PE_1:
        err_list.append(PE_1)
    except FileNotFoundError as FNF_1:
        err_list.append(FNF_1)
    except ValueError as VE_1:
        err_list.append(VE_1)


def hash_computation(file_name: str) -> 'hash result':
    """Returns the value of the MD5 hash function"""
    file_size = pathlib.Path(file_name).stat().st_size
    block_size = 128 ** 4
    if file_size > block_size:
        with open(file_name, 'rb') as file:
            d = hashlib.new('md5')
            while data := file.read(block_size):
                d.update(data)
            return d.hexdigest().upper()
    else:
        with open(file_name, 'rb') as file:
            file = file.read()
            d = hashlib.new('md5')
            d.update(file)
            return d.hexdigest().upper()


exp_list = []  # list of explicit files
rec_list = []  # list of recovered files
exp_hash_table = [[] for i in range(256)]  # hash list of explicit files
error_list = []

while True:
    try:
        exp_path = input('Enter path to directory with explicit files: ')
        rec_path = input('Enter the path to the directory with the deleted files: ')
        if exp_path == rec_path:
            print('Error -> The directories entered match, this will cause a script error')
        elif not pathlib.Path(exp_path).is_dir():
            print('Error -> Directory with explicit files does not exist')
        elif pathlib.Path(exp_path).is_dir() and pathlib.Path(rec_path).is_dir():
            break
        else:
            print('Error -> Directory with deleted files does not exist')
    except PermissionError as PE_2:
        print(PE_2)
    except FileNotFoundError as FNF_2:
        print(FNF_2)

print(start_time(), '-> Folders scan in progress')
folder_scan(exp_path, exp_list, error_list)
folder_scan(rec_path, rec_list, error_list)
print(start_time(), '-> Folders scan completed')

print(start_time(), '-> Creating a hash table in progress')
count = 0
for i in exp_list:
    count += 1
    if count == len(exp_list):
        print('\r', len(exp_list), '|', count)
        count = 0
    else:
        print('\r', len(exp_list), '|', count, end='')
    try:
        result_exp = hash_computation(i)
        index_hex = result_exp[:2]
        index_dec = int(index_hex, 16)
        exp_hash_table[index_dec].append(result_exp)
    except PermissionError as PE_3:
        error_list.append(PE_3)
print(start_time(), '-> Creating a hash table completed')

print(start_time(), '-> Find duplicates in progress')
count_del = 0
for i in rec_list:
    count += 1
    if count == len(rec_list):
        print('\r', len(rec_list), '|', count, '[Duplicates found:' + str(count_del) + ' ]')
        count = 0
    else:
        print('\r', len(rec_list), '|', count, '[Duplicates found:' + str(count_del) + ' ]', end='')
    try:
        result_rec = hash_computation(i)
        index_hex = result_rec[:2]
        index_dec = int(index_hex, 16)
        if result_rec in exp_hash_table[index_dec]:
            count_del += 1
            # pathlib.Path(i).unlink()
    except PermissionError as PE_4:
        error_list.append(PE_4)
print(start_time(), '-> Duplicate search completed')
print('Duplicates removed:', count_del)
print('Runtime errors:', len(error_list))
with open('Errors.log', '+w', encoding='utf-8') as log:
    if not error_list:
        log.write('No errors')
    else:
        for i in error_list:
            log.write(str(i))
print('Done!')
input()  # Comment out for UNIX
