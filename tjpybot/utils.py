############################################################
# GENERAL UTILS FUNCTIONS
############################################################

import pickle
import os


def save(data, tag):
    datafile = open("savedata.p", "wrb")
    if os.stat("savedata.p").st_size == 0:
        datadict = {}
    else:
        datadict = pickle.load(datafile)
    datadict[tag] = data
    pickle.dump(datadict, datafile)
    print(tag + " saved")


def load(tag):
    datafile = open("savedata.p", "rb")
    data = pickle.load(datafile)[tag]
    return data


def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def waitchild(child):
    try:
        child.wait()
    except KeyboardInterrupt:
        try:
            child.terminate()
        except OSError:
            pass
        child.wait()