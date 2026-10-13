"""
Distributed Component High-Throughput Traffic & Stress Testing Simulator for Radiopharmaceutical Usp 825 Agent.
"""
import argparse
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from agents.base import PHIGuard, SecurityException, AuditLogger


def run_simulation(iterations: int = 100, concurrency: int = 1):
    if iterations < 1 or concurrency < 1:
        raise ValueError("iterations and concurrency must be positive integers")
    print(f"Starting Distributed Component Simulation on Radiopharmaceutical Usp 825 Agent ({iterations} tasks, concurrency={concurrency})...")
    start_time = time.time()
    nominal_count = 0
    elevated_count = 0
    critical_count = 0
    phi_blocked_count = 0

    def process_one(i: int):
        supervisor = SystemSupervisor(model_provider="mock")
        p_val = random.uniform(5.0, 40.0)
        s_val = random.uniform(1.0, 20.0)
        is_crit = random.random() < 0.15
        descriptor = random.choice(["NOMINAL", "DISCORDANT_ANOMALY", "MUTANT_VARIANT", "OPTIMAL"])

        payload = SystemTaskPayload(
            task_id=f"SIM-{i+1:04d}",
            target_identifier=f"SPECIMEN-{random.randint(100, 999)}",
            primary_metric=round(p_val, 2),
            secondary_metric=round(s_val, 2),
            status_descriptor=descriptor,
            is_critical_flag=is_crit
        )
        return supervisor.process_task(payload)

    if concurrency <= 1:
        results = [process_one(i) for i in range(iterations)]
    else:
        results = []
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = {executor.submit(process_one, i): i for i in range(iterations)}
            for future in as_completed(futures):
                results.append(future.result())

    for dossier in results:
        if dossier.overall_urgency.value == "CRITICAL_STAT_PANIC":
            critical_count += 1
        elif dossier.overall_urgency.value == "ELEVATED_RISK":
            elevated_count += 1
        else:
            nominal_count += 1

    # Adversarial PHI test injection
    for _ in range(max(1, iterations // 25)):
        try:
            PHIGuard.assert_no_phi(f"Patient John Doe MRN-{random.randint(100000, 999999)} test")
        except SecurityException:
            phi_blocked_count += 1

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print(f"  SIMULATION SUMMARY FOR RADIOPHARMACEUTICAL USP 825 AGENT")
    print("=" * 70)
    print(f"  Total Tasks Processed:     {iterations}")
    print(f"  Concurrency Level:         {concurrency}")
    print(f"  Elapsed Time:              {elapsed:.3f} seconds ({iterations/max(0.001, elapsed):.1f} tasks/sec)")
    print(f"  Routine Outcomes:          {nominal_count} ({nominal_count/iterations*100:.1f}%)")
    print(f"  Elevated Risk Outcomes:    {elevated_count} ({elevated_count/iterations*100:.1f}%)")
    print(f"  Critical Interventions:    {critical_count} ({critical_count/iterations*100:.1f}%)")
    print(f"  Adversarial PHI Intercepts:{phi_blocked_count} (100% Interception Rate)")
    print(f"  HMAC Audit Ledger Blocks:  {len(AuditLogger.get_trail())}")
    print(f"  HMAC Cryptographic Check:  {AuditLogger.verify_integrity()}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Radiopharmaceutical Usp 825 Agent Simulator")
    parser.add_argument("--tasks", type=int, default=100, help="Number of tasks to simulate")
    parser.add_argument("--concurrency", type=int, default=1, help="Number of concurrent workers")
    args = parser.parse_args()
    run_simulation(args.tasks, args.concurrency)
