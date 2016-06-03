#!/usr/bin/env python

def info(*args):
    msg("INFO", args)

def verbose(*args):
    msg("VERB", args)

def error(*args):
    msg("ERR ", args)

def msg(prefix, args):
    for arg in args:
        print(prefix + "> " + str(arg))