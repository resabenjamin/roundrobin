# Round Robin CPU Scheduling: Implementation and Performance Analysis

Operating Systems virtual lab experiment.

## Aim

Implement the Round Robin (RR) CPU scheduling algorithm and analyze its performance for different time quantum values.

## Theory

Round Robin is a **preemptive** scheduling algorithm designed for time-sharing systems.

* The ready queue is a FIFO queue.
* The CPU is given to the process at the front of the queue for at most one **time quantum**.
* If the process finishes within the quantum, it leaves. If not, it is **preempted** and put at the back of the queue.
* A process that arrives while another is running joins the queue before the preempted process is put back.

Performance measures used in this experiment:

| Measure | Formula |
|---|---|
| Turnaround time (TAT) | completion time − arrival time |
| Waiting time (WT) | turnaround time − burst time |
| Response time (RT) | time of first CPU use − arrival time |
| Context switches | number of times the CPU is handed to a different process |
| CPU utilization | total burst time ÷ total elapsed time × 100 |
| Throughput | processes completed ÷ total elapsed time |

## Algorithm

```
ready = empty FIFO queue ; t = 0
add every process with arrival <= t to ready
while some process is unfinished:
    if ready is empty:
        t = arrival time of the next process (CPU idle) ; add arrivals ; continue
    p = remove front of ready
    run = min(quantum, remaining[p])
    if p has not run before: first_run[p] = t
    t = t + run ; remaining[p] = remaining[p] - run
    add every process with arrival <= t to ready        # new arrivals first
    if remaining[p] > 0: add p to the back of ready     # preempted process after them
    else: completion[p] = t
```

An optional **switch cost** adds idle ticks each time the CPU is given to a different process.

## Files

```
round_robin.py   implementation + quantum analysis (console)
index.html       interactive lab: step through the schedule, charts of quantum vs performance
README.md        this report
```

## How to run

Python 3.8 or newer, no dependencies.

```
python round_robin.py                                  # exam workload, quantum 2
python round_robin.py --quantum 4
python round_robin.py --preset textbook --quantum 4    # P1=24, P2=3, P3=3
python round_robin.py --procs "A:0:7,B:2:4,C:4:1,D:5:4" --quantum 3
python round_robin.py --file workload.csv              # lines: name,arrival,burst
python round_robin.py --switch-cost 1                  # include context-switch overhead
```

For the interactive lab, open `index.html` in a browser. It has a **Simulator** tab (ready queue, CPU, Gantt chart, results) and a **Quantum analysis** tab (graphs and table for every quantum value).

## Worked example

Workload: five exam-system tasks, quantum = 2.

| Process | Arrival | Burst |
|---|---|---|
| P1 | 0 | 5 |
| P2 | 1 | 3 |
| P3 | 2 | 8 |
| P4 | 3 | 6 |
| P5 | 4 | 4 |

```
Gantt chart:
| P1 | P2 | P3 | P1 | P4 | P5 | P2 | P3 | P1 | P4 | P5 | P3 | P4 | P3 |
0    2    4    6    8    10   12   13   15   16   18   20   22   24   26

Process  Arrival  Burst  Complete   TAT    WT    RT
P1             0      5        16    16    11     0
P2             1      3        13    12     9     1
P3             2      8        26    24    16     2
P4             3      6        24    21    15     5
P5             4      4        20    16    12     6
```

Average waiting time = 12.60, average turnaround time = 17.80, average response time = 2.80, context switches = 13, CPU utilization = 100% (no idle time), throughput = 0.192 processes per tick.

## Performance analysis: effect of the time quantum

Same workload, quantum from 1 to 8 (8 is the longest burst, so RR behaves exactly like FCFS):

```
Quantum   Avg WT  Avg TAT  Avg RT  Switches  CPU util
      1    12.00    17.20    1.20        24    100.0%
      2    12.60    17.80    2.80        13    100.0%
      3    11.40    16.60    4.40         9    100.0%
      4    12.00    17.20    5.40         7    100.0%
      5    10.00    15.20    6.80         6    100.0%
      6     9.40    14.60    7.40         5    100.0%
      7     9.80    15.00    7.80         5    100.0%
      8     8.20    13.40    8.20         4    100.0%  <- same as FCFS
```

### Observations

1. **Response time gets worse as the quantum grows.** It rises from 1.20 (quantum 1) to 8.20 (quantum 8). A small quantum lets every process start almost immediately.
2. **Context switches fall as the quantum grows.** Quantum 1 needs 24 switches, quantum 8 needs 4. Switches are overhead: with a switch cost of 1 tick, CPU utilization drops from 86.7% (quantum 8) to 52.0% (quantum 1).
3. **Waiting and turnaround time are not smallest at a tiny quantum.** For this workload both are lowest at quantum 8, where RR is the same as FCFS (average waiting time 8.20). RR trades some waiting time for faster response and fairness.
4. **The trend is not perfectly smooth.** For example quantum 3 (11.40) beats quantum 4 (12.00) on waiting time, because where each burst ends relative to the quantum decides how many extra rounds a process needs.
5. **No process starves.** Every process gets the CPU within (number of processes − 1) × quantum ticks of becoming ready.

### Choosing a quantum

* Too small: excellent response, but heavy context-switch overhead.
* Too large: low overhead, but RR degenerates into FCFS and interactive jobs wait behind long ones.
* A good quantum is a little longer than a typical short interactive burst, so most short jobs finish in one turn, while long jobs are still preempted.

## Using the OS virtual lab

To cross-check in the virtual lab, enter the same processes (arrival and burst times) and the same quantum. The values for the worked example above are the ones to compare against: average waiting time 12.60 and average turnaround time 17.80 at quantum 2. Record the virtual lab's Gantt chart and averages next to the tables in this report.

## Conclusion

Round Robin shares the CPU fairly and gives fast response, which makes it well suited to time-sharing and interactive systems. Its performance depends strongly on the time quantum: a very small quantum gives the best response but wastes time on context switches, and a very large quantum turns RR into FCFS with poor response. The quantum should be chosen to balance response time against switching overhead.

## Author

Name: _your name_  
UID: _your UID_  
Class: 5th sem CSE, Section B
