#!/usr/bin/python3

import threading
import requests
import json
import random
import plotly
import plotly.graph_objs as go
import datetime
from acquisitor import *
from analyst import *
from advancedAnalyst import *
from cleaner import *

#API_ENDPOINT = "http://104.155.2.231:3000/api/" #2 PEERS NET
API_ENDPOINT = "http://34.76.123.255:3000/api/" #3 PEERS NET
#API_ENDPOINT = "http://35.241.200.124:3000/api/" #5 PEERS NET
NS = "ertis.uma.nuclear"

#RUN SERVER WITH CARD ADMIN BEFORE EXECUTE THIS FUNCTION
def cleanMultithreading(num_threads, acq, ana, begin=-1, totalDeletes=100):
    threads_acq = []
    threads_ana = []

    if acq == True:
        if begin == -1:
            # Get total number of acquisitions
            resource_url = f"{API_ENDPOINT}{NS}.Acquisitions"
            r = requests.get(resource_url)
            total = len(r.json())
            deletes_per_thread = int(total / num_threads)

            # Create threads
            for i in range(num_threads):
                thread = Cleaner(f"Thread-{i}", 1+deletes_per_thread*i, deletes_per_thread*(i+1), API_ENDPOINT, NS, 1)
                threads_acq.append(thread)
        else:
            deletes_per_thread = int(totalDeletes / num_threads)

            # Create threads
            for i in range(num_threads):
                thread = Cleaner(f"Thread-{i}", begin+deletes_per_thread*i, begin+deletes_per_thread*(i+1)-1, API_ENDPOINT, NS, 1)
                threads_acq.append(thread)

        # Start threads
        for i in range(num_threads):
            threads_acq[i].start()
            
        # Join threads
        for i in range(num_threads):
            threads_acq[i].join()

    if ana == True:
        if begin == -1:
            # Get total number of analysis
            resource_url = f"{API_ENDPOINT}{NS}.Analysis"
            r = requests.get(resource_url)
            total = len(r.json())
            deletes_per_thread = int(total / num_threads)

            # Create threads
            for i in range(num_threads):
                thread = Cleaner(f"Thread-{i}", 1+deletes_per_thread*i, deletes_per_thread*(i+1), API_ENDPOINT, NS, 2)
                threads_ana.append(thread)
        else:
            deletes_per_thread = int(totalDeletes / num_threads)

            # Create threads
            for i in range(num_threads):
                thread = Cleaner(f"Thread-{i}", begin+deletes_per_thread*i, begin+deletes_per_thread*(i+1)-1, API_ENDPOINT, NS, 2)
                threads_ana.append(thread)

        # Start threads
        for i in range(num_threads):
            threads_ana[i].start()
            
        # Join threads
        for i in range(num_threads):
            threads_ana[i].join()

def addTubes(n_tubes):
    # Check for next tube id
    resource_url = f"{API_ENDPOINT}{NS}.Tube"
    r = requests.get(resource_url)
    next_id = len(r.json()) + 1

    resource_url = f"{API_ENDPOINT}{NS}.RegisterTube"

    for i in range(n_tubes):
        data = {
            "tubeId": i+next_id,
            "posX": random.randint(0, 100),
            "posY": random.randint(0, 100),
            "length": random.randint(5, 20)
        }
        r = requests.post(resource_url, data=data)
        if r.status_code == requests.codes.ok:
            print(f"Added tube {i+next_id}")
        else:
            print(f"Error when adding tube {i+next_id}")

def addWorkAndCalibrations():
    #Create work 1
    resource_url = f"{API_ENDPOINT}{NS}.CreateWork"
    data = {
        "workId": "1",
        "workDate": generateDateTime(),
        "description": "Testing"
    }
    r = requests.post(resource_url, data=data)
    if r.status_code == requests.codes.ok:
        print(f"Work 1 created")
    else:
        print(f"Error when creating work 1")

    # Check how many tubes exist
    resource_url = f"{API_ENDPOINT}{NS}.Tube"
    r = requests.get(resource_url)
    n_tubes = len(r.json())
    n_calibrations = int(n_tubes / 25)

    resource_url = f"{API_ENDPOINT}{NS}.AddCalibration"
    for i in range(1, n_calibrations+1):
        #Add calibration i
        data = {
            "calId": i,
            "calDate": generateDateTime(),
            "equipment": "DRONE",
            "workId": "1"
        }
        r = requests.post(resource_url, data=data)
        if r.status_code == requests.codes.ok:
            print(f"Added calibration {i}")
        else:
            print(f"Error when adding calibration {i}")

def getCalibrations(role):
    # Check how many calibrations exist
    resource_url = f"{API_ENDPOINT}{NS}.Calibration"
    r = requests.get(resource_url)
    n_calibrations = len(r.json())
    
    resource_url = f"{API_ENDPOINT}{NS}.GetCalibration"
    for i in range(1, n_calibrations+1):
        #Add calibration i
        data = {
            "calId": i,
            "type": role
        }
        r = requests.post(resource_url, data=data)
        if r.status_code == requests.codes.ok:
            print(f"Gotten calibration {i}")
        else:
            print(f"Error when getting calibration {i}")

def addAcquisitionTest(num_acquisitors, num_tubes):
    acquisitor_threads = []
    acquisitions_per_worker = int(num_tubes/num_acquisitors)

    # Check for next acquisition id
    resource_url = f"{API_ENDPOINT}{NS}.Acquisition"
    r = requests.get(resource_url)
    next_id = len(r.json()) + 1

    # Create threads
    for i in range(num_acquisitors):
        thread = Acquisitor(i, f"Acquisitor-{i}", acquisitions_per_worker, next_id+acquisitions_per_worker*i, API_ENDPOINT, NS)
        acquisitor_threads.append(thread)

    # Start threads
    for i in range(num_acquisitors):
        acquisitor_threads[i].start()

    # Join threads
    for i in range(num_acquisitors):
        acquisitor_threads[i].join()
        
    # Print results
    min = acquisitor_threads[0].min
    min5avg = acquisitor_threads[0].min5avg
    avg = acquisitor_threads[0].avg
    max = acquisitor_threads[0].max
    max5avg = acquisitor_threads[0].max5avg
    acquisitor_threads[0].printResults()
    for i in range(1, num_acquisitors):
        if acquisitor_threads[i].min < min:
            min = acquisitor_threads[i].min
            
        min5avg = min5avg + acquisitor_threads[i].min5avg

        avg = avg + acquisitor_threads[i].avg

        if acquisitor_threads[i].max > max:
            max = acquisitor_threads[i].max
            
        max5avg = max5avg + acquisitor_threads[i].max5avg

        acquisitor_threads[i].printResults()

    print(f"MIN --> {min}")
    print(f"MIN 5 AVG --> {min5avg/num_acquisitors}")
    print(f"AVG --> {avg/num_acquisitors}")
    print(f"MAX --> {max}")
    print(f"MAX 5 AVG --> {max5avg/num_acquisitors}")

def addAnalysisTest(num_analysts, num_acqs):
    analyst_threads = []
    analysis_per_worker = int(num_acqs/num_analysts)
    
    # Check for next analysis id
    resource_url = f"{API_ENDPOINT}{NS}.Analysis"
    r = requests.get(resource_url)
    next_id = len(r.json()) + 1
    
    # Create threads
    for i in range(num_analysts):
        thread = Analyst(i, f"Analyst-{i}", analysis_per_worker, next_id+analysis_per_worker*i, API_ENDPOINT, NS)
        analyst_threads.append(thread)
        
    # Start threads
    for i in range(num_analysts):
        analyst_threads[i].start()
        
    # Join threads
    for i in range(num_analysts):
        analyst_threads[i].join()
        
    # Print results
    min_get = analyst_threads[0].min_get
    if num_analysts <= 10:
        min5avg_get = analyst_threads[0].min5avg_get
    avg_get = analyst_threads[0].avg_get
    max_get = analyst_threads[0].max_get
    if num_analysts <= 10:
        max5avg_get = analyst_threads[0].max5avg_get
    
    min_add = analyst_threads[0].min_add
    if num_analysts <= 10:
        min5avg_add = analyst_threads[0].min5avg_add
    avg_add = analyst_threads[0].avg_add
    max_add = analyst_threads[0].max_add
    if num_analysts <= 10:
        max5avg_add = analyst_threads[0].max5avg_add
    
    analyst_threads[0].printResults()
    for i in range(1, num_analysts):
        if analyst_threads[i].min_get < min_get:
            min_get = analyst_threads[i].min_get
        
        if num_analysts <= 10:
            min5avg_get = min5avg_get + analyst_threads[i].min5avg_get

        avg_get = avg_get + analyst_threads[i].avg_get

        if analyst_threads[i].max_get > max_get:
            max_get = analyst_threads[i].max_get
            
        if num_analysts <= 10:
            max5avg_get = max5avg_get + analyst_threads[i].max5avg_get
            
        if analyst_threads[i].min_add < min_add:
            min_add = analyst_threads[i].min_add
            
        if num_analysts <= 10:
            min5avg_add = min5avg_add + analyst_threads[i].min5avg_add
            
        avg_add = avg_add + analyst_threads[i].avg_add
        
        if analyst_threads[i].max_get > max_get:
            max_add = analyst_threads[i].max_add
        
        if num_analysts <= 10:
            max5avg_add = max5avg_add + analyst_threads[i].max5avg_add

        analyst_threads[i].printResults()

    print(f"MIN GET ACQ --> {min_get}")
    if num_analysts <= 10:
        print(f"MIN 5 GET ACQ --> {min5avg_get/num_analysts}")
    print(f"AVG GET ACQ --> {avg_get/num_analysts}")
    print(f"MAX GET ACQ --> {max_get}")
    if num_analysts <= 10:
        print(f"MAX 5 GET ACQ --> {max5avg_get/num_analysts}")
    
    print(f"MIN ADD ANA --> {min_add}")
    if num_analysts <= 10:
        print(f"MIN 5 GET ANA --> {min5avg_add/num_analysts}")
    print(f"AVG ADD ANA --> {avg_add/num_analysts}")
    print(f"MAX ADD ANA --> {max_add}")
    if num_analysts <= 10:
        print(f"MAX 5 GET ANA --> {max5avg_add/num_analysts}")

    print("Add Analysis Test Finalized")

def addResolutionTest(num_analysts, num_acqs):
    analyst_threads = []
    analysis_per_worker = int(num_acqs/num_analysts)
    
    # Check for next analysis id
    resource_url = f"{API_ENDPOINT}{NS}.Analysis"
    r = requests.get(resource_url)
    next_id = len(r.json()) + 1
    
    # Create threads
    for i in range(num_analysts):
        thread = AdvancedAnalyst(i, f"Advanced Analyst-{i}", analysis_per_worker, next_id+analysis_per_worker*i, API_ENDPOINT, NS)
        analyst_threads.append(thread)
        
    # Start threads
    for i in range(num_analysts):
        analyst_threads[i].start()
        
    # Join threads
    for i in range(num_analysts):
        analyst_threads[i].join()
        
    # Print results
    min_get_acq = analyst_threads[0].min_get_acq
    if num_analysts <= 10:
        min5avg_get_acq = analyst_threads[0].min5avg_get_acq
    avg_get_acq = analyst_threads[0].avg_get_acq
    max_get_acq = analyst_threads[0].max_get_acq
    if num_analysts <= 10:
        max5avg_get_acq = analyst_threads[0].max5avg_get_acq
    
    min_get_ana = analyst_threads[0].min_get_ana
    if num_analysts <= 10:
        min5avg_get_ana = analyst_threads[0].min5avg_get_ana
    avg_get_ana = analyst_threads[0].avg_get_ana
    max_get_ana = analyst_threads[0].max_get_ana
    if num_analysts <= 10:
        max5avg_get_ana = analyst_threads[0].max5avg_get_ana
    
    min_add = analyst_threads[0].min_add
    if num_analysts <= 10:
        min5avg_add = analyst_threads[0].min5avg_add
    avg_add = analyst_threads[0].avg_add
    max_add = analyst_threads[0].max_add
    if num_analysts <= 10:
        max5avg_add = analyst_threads[0].max5avg_add
    
    analyst_threads[0].printResults()
    for i in range(1, num_analysts):
        if analyst_threads[i].min_get_acq < min_get_acq:
            min_get_acq = analyst_threads[i].min_get_acq
        
        if num_analysts <= 10:
            min5avg_get_acq = min5avg_get_acq + analyst_threads[0].min5avg_get_acq

        avg_get_acq = avg_get_acq + analyst_threads[i].avg_get_acq

        if analyst_threads[i].max_get_acq > max_get_acq:
            max_get_acq = analyst_threads[i].max_get_acq
        
        if num_analysts <= 10:
            max5avg_get_acq = max5avg_get_acq + analyst_threads[0].max5avg_get_acq
        
        if analyst_threads[i].min_get_ana < min_get_ana:
            min_get_ana = analyst_threads[i].min_get_ana
        
        if num_analysts <= 10:
            min5avg_get_ana = min5avg_get_ana + analyst_threads[0].min5avg_get_ana

        avg_get_ana = avg_get_ana + analyst_threads[i].avg_get_ana

        if analyst_threads[i].max_get_ana > max_get_ana:
            max_get_ana = analyst_threads[i].max_get_ana
        
        if num_analysts <= 10:
            max5avg_get_ana = max5avg_get_ana + analyst_threads[0].max5avg_get_ana
            
        if analyst_threads[i].min_add < min_add:
            min_add = analyst_threads[i].min_add
            
        if num_analysts <= 10:
            min5avg_add = min5avg_add + analyst_threads[0].min5avg_add
            
        avg_add = avg_add + analyst_threads[i].avg_add
        
        if analyst_threads[i].max_add > max_add:
            max_add = analyst_threads[i].max_add
        
        if num_analysts <= 10:
            max5avg_add = max5avg_add + analyst_threads[0].max5avg_add

        analyst_threads[i].printResults()

    print(f"MIN GET ACQ --> {min_get_acq}")
    if num_analysts <= 10:
        print(f"MIN 5 GET ACQ --> {min5avg_get_acq/num_analysts}")
    print(f"AVG GET ACQ --> {avg_get_acq/num_analysts}")
    print(f"MAX GET ACQ --> {max_get_acq}")
    if num_analysts <= 10:
        print(f"MAX 5 GET ACQ --> {max5avg_get_acq/num_analysts}")
    
    print(f"MIN GET ANA --> {min_get_ana}")
    if num_analysts <= 10:
        print(f"MIN 5 GET ANA --> {min5avg_get_ana/num_analysts}")
    print(f"AVG GET ANA --> {avg_get_ana/num_analysts}")
    print(f"MAX GET ANA --> {max_get_ana}")
    if num_analysts <= 10:
        print(f"MAX 5 GET ANA --> {max5avg_get_ana/num_analysts}")
    
    print(f"MIN ADD ANA --> {min_add}")
    if num_analysts <= 10:
        print(f"MIN 5 ADD ANA --> {min5avg_add/num_analysts}")
    print(f"AVG ADD ANA --> {avg_add/num_analysts}")
    print(f"MAX ADD ANA --> {max_add}")
    if num_analysts <= 10:
        print(f"MAX 5 ADD ANA --> {max5avg_add/num_analysts}")

    print("Add Resolution Test Finalized")

def generateDateTime():
    x = str(datetime.datetime.now()).replace(" ", "T")
    x2 = x[:len(x)-3]+"Z"

    return x2

#cleanMultithreading(10, True, False, 1)
#addTubes(250)
#addWorkAndCalibrations()
#addAcquisitionTest(1, 500) #Acquisitors, Acquisitions to do
#getCalibrations('PRIMARY')
#getCalibrations('SECONDARY')
#addAnalysisTest(10, 500) #Analysts, Analysis to do
#getCalibrations('RESOLUTION')
#addResolutionTest(1, 500)

