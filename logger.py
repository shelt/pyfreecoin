#!/usr/bin/env python

def info(body):
    msg("INFO", body)

def verbose(body):
    msg("VERB", body)

def error(body):
    msg("ERR ", body)

def msg(prefix, body):
    if type(body) == list:
        lines = body
    elif "\n" in body:
        lines = body.split("\n")
    else:
        lines = [body]

    for line in lines:
        print(prefix + "> " + line)
