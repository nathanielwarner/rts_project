#!/usr/bin/env python

"""
fifo.py - First-In First-Out scheduler

FifoPriorityQueue: priority queue that prioritizes by release time
FifoScheduler: scheduling algorithm that executes FIFO (non-preemptive)
"""

import json
import sys

from taskset import *
from scheduleralgorithm import *
from schedule import ScheduleInterval, Schedule
from window import *

class FifoPriorityQueue(PriorityQueue):
    def __init__(self, jobReleaseDict):
        """
        Creates a priority queue of jobs ordered by release time.
        """
        PriorityQueue.__init__(self, jobReleaseDict)

    def _sortQueue(self):
        # FIFO orders by release time
        self.jobs.sort(key = lambda x: (x.releaseTime, x.task.id))

    def _findFirst(self, t):
        """
        Returns the index of the highest-priority job released at or before t,
        or -1 if the queue is empty or if all remaining jobs are released after t.
        """
        if self.isEmpty():
            return -1

        if self.jobs[0].releaseTime > t:
            return -1

        return 0

    def popNextJob(self, t):
        """
        Removes and returns the highest-priority job of those released at or after t,
        or None if no jobs are released at or after t.
        """
        if not self.isEmpty() and self.jobs[0].releaseTime >= t:
            return self.jobs.pop(0)
        else:
            return None

    def popPreemptingJob(self, t, job):
        """
        Removes and returns the job that will preempt job 'job' after time 't', or None
        if no such preemption will occur (i.e., if no higher-priority jobs
        are released before job 'job' will finish executing).

        t: the time after which a preemption may occur
        job: the job that is executing at time 't', and which may be preempted
        """
        return None

class FifoScheduler(SchedulerAlgorithm):
    def __init__(self, taskSet):
        SchedulerAlgorithm.__init__(self, taskSet)

    def buildSchedule(self, startTime, endTime):
        self._buildPriorityQueue(FifoPriorityQueue)

        time = 0.0
        self.schedule.startTime = time

        previousJob = None
        didPreemptPrevious = False # should stay false due to FIFO

        # Loop until the priority queue is empty, executing jobs non-preemptively in FIFO order
        while not self.priorityQueue.isEmpty():
            # Make a scheduling decision resulting in an interval
            interval, newJob = self._makeSchedulingDecision(time, previousJob)

            nextTime = interval.startTime
            didPreemptPrevious = interval.didPreemptPrevious # should be False

            if didPreemptPrevious:
                print("ERROR!  FIFO is meant to be non-preemptive!")
                return None

            # If the previous interval wasn't idle, execute the previous job to completion
            # until the start of the new interval
            if previousJob is not None:
                previousJob.executeToCompletion()

            # Add the interval to the schedule
            self.schedule.addInterval(interval)

            # Update the time and job
            time = nextTime
            previousJob = newJob

        # If there is still a previous job, complete it and update the time
        if previousJob is not None:
            time += previousJob.remainingTime
            previousJob.executeToCompletion()

        # Add the final idle interval
        finalInterval = ScheduleInterval()
        finalInterval.intialize(time, None, False)
        self.schedule.addInterval(finalInterval)

        # Post-process the intervals to set the end time and whether the job completed
        latestDeadline = max([job.deadline for job in self.taskSet.jobs])
        endTime = max(time + 1.0, latestDeadline, float(endTime))
        self.schedule.postProcessIntervals(endTime)

        return self.schedule

    def _makeSchedulingDecision(self, t, previousJob):
        """
        Makes a scheduling decision after time t.

        t: the beginning of the previous time interval, if one exists (or 0 otherwise)
        previousJob: the job that was previously executing, and will either complete or be preempted

        returns: (ScheduleInterval instance, Job instance of new job to execute)
        """
        if previousJob is None:
            # If there was no previous job, the last interval was an idle one
            newJob = self.priorityQueue.popNextJob(t)
            nextTime = newJob.releaseTime
        else:
            # There are no preemptions, so try to find a new job to executed
            # after the current one finishes
            intervalDuration = previousJob.remainingTime
            nextTime = t + intervalDuration

            # Choose a new job to execute (if None, this will be an idle interval)
            newJob = self.priorityQueue.popFirst(nextTime)

        # Build the schedule interval
        interval = ScheduleInterval()
        interval.intialize(nextTime, newJob, False) # no preemptions under FIFO

        return interval, newJob

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "tasksets/test1.json"

    with open(file_path) as json_data:
        data = json.load(json_data)

    taskSet = TaskSet(data)

    taskSet.printTasks()
    taskSet.printJobs()

    scheduleStartTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_START])
    scheduleEndTime = float(data[TaskSetJsonKeys.KEY_SCHEDULE_END])

    fifo = FifoScheduler(taskSet)
    schedule = fifo.buildSchedule(scheduleStartTime, scheduleEndTime)

    schedule.printIntervals(displayIdle=True)

    print("\n// Validating the schedule:")
    schedule.checkWcets()
    schedule.checkFeasibility()

    display = Window()
    display.execute(schedule)