#!/usr/bin/env python
# coding: utf8

import os
from datetime import datetime

LOG_PATH = "../logs/"

class Log:

    def __init__(self, msg, type = "INFO"):

        #get time
        now = datetime.now()
        date_time = "[" + now.strftime("%m/%d/%Y %H:%M:%S.%f") + "] "

        with open(os.path.dirname(os.path.abspath(__file__)) + "/" + LOG_PATH + "app.log", "a+") as f:
            f.write(date_time + type + ": " + msg + "\n")