#!/usr/bin/python3

import threading
import time
import requests
import json
import random

class Analyst(threading.Thread):

    def __init__(self, thread_id, analyst_name, times, begin, API_ENDPOINT, NS, DEBUG = False):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.analyst_name = analyst_name
        self.times = times
        self.begin = begin
        self.API_ENDPOINT = API_ENDPOINT
        self.NS = NS
        self.DEBUG = DEBUG

    def run(self):
        print(f"Analyst {self.analyst_name} has started")
        results = self.addMultipleAnalysis()
        print(f"Analyst {self.analyst_name} has finished")

    def addMultipleAnalysis(self):
        time_list = []
        time_list2 = []
        for i in range(self.begin, self.begin+self.times):
            acqId = i%100
            if acqId == 0:
                acqId = 100
            acq = self.getAcquisition(acqId)
            time_list.append(acq[0])
            if self.DEBUG:
                print(f"Analyst-{self.analyst_name} --> Analyzing {acq[1]}")
            analysis = self.addAnalysis(i)
            time_list2.append(analysis)
            
        self.min_get = min(time_list)
        self.avg_get = sum(time_list)/self.times
        self.max_get = max(time_list)

        self.min_add = min(time_list2)
        self.avg_add = sum(time_list2)/self.times
        self.max_add = max(time_list2)


    def getAcquisition(self, acqId):
        start_time = time.time()
        r = requests.get(f"{self.API_ENDPOINT}{self.NS}.Acquisition/{acqId}")
        elapsed_time = time.time() - start_time
        if self.DEBUG:
            print(r.json()['filename'])
        return (elapsed_time, r.json()['filename'])

    def addAnalysis(self, anaId):
        resource_url = f"{self.API_ENDPOINT}{self.NS}.AddAnalysis"
        acqId = anaId%100
        if acqId == 0:
            acqId = 100
        data = {
            "analysisId": anaId,
            "method": "MANUAL",
            "acqId": acqId,
            "indications": []
        }
        start_time = time.time()
        r = requests.post(resource_url, data=data)
        elapsed_time = time.time() - start_time
        if self.DEBUG:
            print(f"Elapsed time: {elapsed_time}")
            print(f"Response status code: {r.status_code}")
            print(r.json())
        return elapsed_time

    def printResults(self):
        print(f"{self.analyst_name} - Fastest acquisition gotten in {self.min_get} seconds")
        print(f"{self.analyst_name} - Slowest acquisition gotten in {self.max_get} seconds")
        print(f"{self.analyst_name} - Average time getting acquisitions: {self.avg_get} seconds")

        print(f"{self.analyst_name} - Fastest analysis added in {self.min_add} seconds")
        print(f"{self.analyst_name} - Slowest analysis added in {self.max_add} seconds")
        print(f"{self.analyst_name} - Average time adding analysis: {self.avg_add} seconds")
