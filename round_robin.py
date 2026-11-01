#!/usr/bin/env python3
"""
Round Robin CPU scheduling: implementation and performance analysis.

Round Robin gives every ready process the CPU for at most one time quantum.
A process that has not finished is put at the back of the ready queue.

For one quantum the program prints the Gantt chart and, for each process:
completion, turnaround (TAT), waiting (WT) and response time (RT), plus
context switches, CPU utilization and throughput. It then sweeps the quantum
from 1 upward to show how the quantum affects performance.

Usage:
    python round_robin.py                              # exam-system workload, quantum 2
    python round_robin.py --quantum 4
    python round_robin.py --preset textbook --quantum 4
    python round_robin.py --procs "A:0:7,B:2:4,C:4:1,D:5:4" --quantum 3
    python round_robin.py --file workload.csv          # CSV lines: name,arrival,burst
    python round_robin.py --switch-cost 1              # context-switch overhead in ticks
"""
import argparse
from collections import deque

PRESETS = {
    "exam": [("P1", 0, 5), ("P2", 1, 3), ("P3", 2, 8), ("P4", 3, 6), ("P5", 4, 4)],
    "textbook": [("P1", 0, 24), ("P2", 0, 3), ("P3", 0, 3)],
    "classic": [("A", 0, 7), ("B", 2, 4), ("C", 4, 1), ("D", 5, 4)],
}


def round_robin(procs, quantum, switch_cost=0):
    """procs: list of (name, arrival, burst). Returns (segments, per-process results, summary).

    segments: (label, start, end) where label is a process index, 'idle' or 'switch'.
    """
    n = len(procs)
    order = sorted(range(n), key=lambda i: (procs[i][1], i))   # by arrival, then input order
    remaining = [p[2] for p in procs]
    first_run = [None] * n
    completion = [0] * n
    segments, ready = [], deque()
    t, nxt, done, last, switches = 0, 0, 0, None, 0

    def admit():
        nonlocal nxt
        while nxt < n and procs[order[nxt]][1] <= t:
            ready.append(order[nxt])
            nxt += 1

    admit()
    while done < n:
        if not ready:                                   # CPU idle until the next arrival
            jump = procs[order[nxt]][1]
            segments.append(("idle", t, jump))
            t, last = jump, None
            admit()
            continue
        i = ready.popleft()
        if last is not None and last != i:              # CPU handed to a different process
            switches += 1
            if switch_cost:
                segments.append(("switch", t, t + switch_cost))
                t += switch_cost
                admit()
        if first_run[i] is None:
            first_run[i] = t
        run = min(quantum, remaining[i])
        segments.append((i, t, t + run))
        t += run
        remaining[i] -= run
        admit()                                         # arrivals during the slice queue first
        if remaining[i] > 0:
            ready.append(i)                             # preempted: back of the queue
        else:
            completion[i] = t
            done += 1
        last = i

    merged = []                                         # join back-to-back slices of one process
    for lab, s, e in segments:
        if merged and merged[-1][0] == lab and merged[-1][2] == s and lab not in ("idle", "switch"):
            merged[-1] = (lab, merged[-1][1], e)
        else:
            merged.append((lab, s, e))

    rows = []
    for i, (name, at, bt) in enumerate(procs):
        tat = completion[i] - at
        rows.append({"name": name, "at": at, "bt": bt, "ct": completion[i],
                     "tat": tat, "wt": tat - bt, "rt": first_run[i] - at})
    makespan = max(completion)
    busy = sum(p[2] for p in procs)
    summary = {
        "avg_wt": sum(r["wt"] for r in rows) / n,
        "avg_tat": sum(r["tat"] for r in rows) / n,
        "avg_rt": sum(r["rt"] for r in rows) / n,
        "switches": switches,
        "makespan": makespan,
        "utilization": 100.0 * busy / makespan,
        "throughput": n / makespan,
    }
    return merged, rows, summary


def gantt(segments, procs):
    bar, axis = "|", ""
    for lab, s, e in segments:
        name = {"idle": "idle", "switch": "cs"}.get(lab, None) or procs[lab][0]
        width = max(len(name) + 2, len(str(s)) + 1)
        bar += name.center(width) + "|"
        axis += str(s).ljust(width + 1)
    return bar + "\n" + axis + str(segments[-1][2])


def show_run(procs, quantum, switch_cost):
    segs, rows, sm = round_robin(procs, quantum, switch_cost)
    print(f"ROUND ROBIN, quantum = {quantum}" + (f", switch cost = {switch_cost}" if switch_cost else ""))
    print("=" * 66)
    print("Gantt chart:\n" + gantt(segs, procs) + "\n")
    print(f"{'Process':<8}{'Arrival':>8}{'Burst':>7}{'Complete':>10}{'TAT':>6}{'WT':>6}{'RT':>6}")
    for r in rows:
        print(f"{r['name']:<8}{r['at']:>8}{r['bt']:>7}{r['ct']:>10}{r['tat']:>6}{r['wt']:>6}{r['rt']:>6}")
    print(f"\nAverage waiting time    : {sm['avg_wt']:.2f}")
    print(f"Average turnaround time : {sm['avg_tat']:.2f}")
    print(f"Average response time   : {sm['avg_rt']:.2f}")
    print(f"Context switches        : {sm['switches']}")
    print(f"CPU utilization         : {sm['utilization']:.1f}%")
    print(f"Throughput              : {sm['throughput']:.3f} processes per tick\n")


def sweep(procs, switch_cost):
    top = max(p[2] for p in procs)
    print("PERFORMANCE VS TIME QUANTUM")
    print("=" * 66)
    print(f"{'Quantum':>7}{'Avg WT':>9}{'Avg TAT':>9}{'Avg RT':>8}{'Switches':>10}{'CPU util':>10}")
    results = []
    for q in range(1, top + 1):
        _, _, sm = round_robin(procs, q, switch_cost)
        results.append((q, sm))
        note = "  <- same as FCFS" if q == top else ""
        print(f"{q:>7}{sm['avg_wt']:>9.2f}{sm['avg_tat']:>9.2f}{sm['avg_rt']:>8.2f}"
              f"{sm['switches']:>10}{sm['utilization']:>9.1f}%{note}")
    best_wt = min(results, key=lambda r: (r[1]["avg_wt"], r[0]))
    best_rt = min(results, key=lambda r: (r[1]["avg_rt"], r[0]))
    q1, qn = results[0][1], results[-1][1]
    print("\nObservations")
    print(f"- Lowest average waiting time: {best_wt[1]['avg_wt']:.2f} at quantum {best_wt[0]}.")
    print(f"- Lowest average response time: {best_rt[1]['avg_rt']:.2f} at quantum {best_rt[0]}.")
    print(f"- Quantum 1 needs {q1['switches']} context switches; quantum {top} (FCFS) needs {qn['switches']}.")
    print(f"- Average response time grows from {q1['avg_rt']:.2f} (quantum 1) to {qn['avg_rt']:.2f} (quantum {top}).")
    if best_wt[0] == top:
        print("- Waiting time is lowest when the quantum is large enough to act like FCFS: "
              "Round Robin trades some waiting time for a faster first response.")
    if switch_cost:
        print(f"- With a switch cost of {switch_cost}, CPU utilization falls from {qn['utilization']:.1f}% "
              f"(quantum {top}) to {q1['utilization']:.1f}% (quantum 1).")


def parse_procs(text):
    out = []
    for k, part in enumerate(text.split(","), 1):
        bits = part.strip().split(":")
        name, at, bt = (bits if len(bits) == 3 else (f"P{k}", bits[0], bits[1]))
        out.append((name, int(at), int(bt)))
    return out


def main():
    ap = argparse.ArgumentParser(description="Round Robin CPU scheduling")
    ap.add_argument("--quantum", type=int, default=2)
    ap.add_argument("--preset", choices=PRESETS, default="exam")
    ap.add_argument("--procs", help='custom workload, e.g. "A:0:7,B:2:4" (name:arrival:burst)')
    ap.add_argument("--file", help="CSV file with lines name,arrival,burst")
    ap.add_argument("--switch-cost", type=int, default=0, help="ticks lost on each context switch")
    args = ap.parse_args()
    if args.file:
        with open(args.file) as f:
            procs = [(a, int(b), int(c)) for a, b, c in (l.strip().split(",") for l in f if l.strip())]
    elif args.procs:
        procs = parse_procs(args.procs)
    else:
        procs = PRESETS[args.preset]
    if args.quantum < 1 or any(p[2] < 1 or p[1] < 0 for p in procs):
        ap.error("quantum and burst times must be at least 1, arrival times at least 0")
    show_run(procs, args.quantum, args.switch_cost)
    sweep(procs, args.switch_cost)


if __name__ == "__main__":
    main()
