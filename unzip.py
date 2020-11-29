#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time: 2020/11/22 17:30
# @Author: qyh

import os
import argparse
import zipfile
import rarfile
import itertools
import threading


words = ' abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~!@#$%^&*()_-+=/*<>:;\'"[]{}|'
multi_threads_flag = True


def try_compressed_pwd(compressed_file, password, save_path):
    try:
        compressed_file.extractall(path=save_path, pwd=password.encode('utf-8'))
        print(f"[+] Compressed File decompression success, password: {password}")
        return True
    except:
        print(f"[-] Compressed File decompression failed, password: {password}")
        return False


def get_save_path(compressed_file):
    path, file = os.path.split(compressed_file)
    dir_name = file.split('.')[0]
    dir_path = os.path.join(path, dir_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    return dir_path


def decompress_with_pwd_file(compressed_file, pwd_file):
    success = False
    with open(pwd_file) as pwd_f:
        if compressed_file.endswith('.zip'):
            fp = zipfile.ZipFile(compressed_file)
        else:
            fp = rarfile.RarFile(compressed_file)

        dir_path = get_save_path(compressed_file)
        for pwd in pwd_f.readlines():
            success = try_compressed_pwd(fp, pwd.strip('\n'), dir_path)
            if success:
                fp.close()
                break
    if not success:
        fp.close()


def get_password(min_digits_len, max_digit_len, words):
    while min_digits_len <= max_digit_len:
        pwds = itertools.product(words, repeat=min_digits_len)
        for pwd in pwds:
            yield ''.join(pwd)
        min_digits_len += 1


def multi_threads_extract(file_ptr, save_path, passwords):
    global multi_threads_flag
    while multi_threads_flag:
        password = next(passwords)
        try:
            file_ptr.extractall(path=save_path, pwd=password.encode('utf-8'))
            print(f"[+] Compressed File decompression success, password: {password}")
            multi_threads_flag = False
            break
        except:
            print(f"[-] Compressed File decompression failed, password: {password}")


def decompress_without_pwd_file(compressed_file):
    global words
    passwords = get_password(4, 12, words)
    save_path = get_save_path(compressed_file)
    if compressed_file.endswith('.zip'):
        fp = zipfile.ZipFile(compressed_file)
    else:
        fp = rarfile.RarFile(compressed_file)
    for _ in range(3):
        t = threading.Thread(target=multi_threads_extract, args=(fp, save_path, passwords))
        t.start()


def main():
    parser = argparse.ArgumentParser(description="Crack ZIP/RAR File")
    parser.add_argument('-f', dest='compressed_file', type=str, help="The zip/rar file path.")
    parser.add_argument('-w', dest='pwd_file', type=str, help="Password dictionary file.")
    compressed_file_path = None
    pwd_file_path = None
    try:
        options = parser.parse_args()
        compressed_file_path = options.compressed_file
        pwd_file_path = options.pwd_file
    except:
        print(parser.parse_args(['-h']))
        exit(0)

    if compressed_file_path is None:
        print(parser.parse_args(['-h']))
        exit(0)

    if not compressed_file_path.endswith('.rar') and not compressed_file_path.endswith('.zip'):
        print('Must be Rar or Zip file')
        exit(0)

    if pwd_file_path is None:
        decompress_without_pwd_file(compressed_file_path)
    else:
        decompress_with_pwd_file(compressed_file_path, pwd_file_path)


if __name__ == '__main__':
    main()
