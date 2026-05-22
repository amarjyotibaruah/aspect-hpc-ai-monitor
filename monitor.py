"""Main monitoring workflow script for aspect-hpc-ai-monitor."""


import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from ai.ai_diagnoser import AIDiagnoser
from parsers.aspect_log_parser import AspectLogParser
from analyzers.simulation_analyzer import SimulationAnalyzer
from reports.report_generator import ReportGenerator
from hpc.ssh_connector import SSHConnector
from hpc.slurm_checker import SlurmChecker
from hpc.remote_log_reader import RemoteLogReader


def run_local_monitor(log_file):
    """Run local ASPECT log parsing, analysis, and report generation."""

    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)

    print(f"Processing local log file: {log_file}")

    print("\n[1/4] Parsing log file...")
    parser = AspectLogParser(log_file)
    log_data = parser.read_log()

    if log_data is None:
        print("Error: Failed to read log file")
        sys.exit(1)

    parser_summary = parser.summarize()
    print(f"  - Total lines: {parser_summary['total_lines']}")
    print(f"  - Errors found: {parser_summary['errors_count']}")
    print(f"  - Timesteps found: {parser_summary['timesteps_count']}")

    print("\n[2/4] Analyzing simulation data...")
    analyzer = SimulationAnalyzer(parser)
    analyzer.analyze()

    analyzer_summary = analyzer.get_summary()
    print(f"  - Total errors: {analyzer_summary['total_errors']}")
    print(f"  - Convergence issues: {analyzer_summary['convergence_issues']}")
    print(f"  - Memory issues: {analyzer_summary['memory_issues']}")
    print(f"  - NaN occurrences: {analyzer_summary['nan_count']}")

    print("\n[3/4] Generating report...")
    generator = ReportGenerator(parser, analyzer)
    markdown_report_path = generator.generate_markdown_report()

    print("\n[4/4] Workflow complete")
    print(f"\n✓ Report saved to: {markdown_report_path}")


def run_remote_monitor(job_id=None):
    """Connect to remote HPC cluster and check Slurm job status."""

    print("Connecting to remote HPC cluster...")

    with SSHConnector() as connector:
        if not connector.check_connection():
            print("Error: SSH connection check failed.")
            sys.exit(1)

        print("✓ SSH connection successful")

        username = os.getenv("HPC_USERNAME")
        checker = SlurmChecker(connector)

        print("\n[1/3] Checking active Slurm jobs...")
        active_jobs = checker.get_user_jobs(username)
        print(active_jobs)

        print("\n[2/3] Checking recent Slurm jobs...")
        recent_jobs = checker.get_recent_jobs(username)
        print(recent_jobs)

        if job_id:
            print(f"\n[3/3] Checking job ID: {job_id}")
            job_status = checker.check_job(job_id)
            print(job_status)
        else:
            print("\n[3/3] No job ID provided. Skipping individual job check.")

    print("\n✓ Remote Slurm check complete")


def run_remote_log_monitor(remote_log_path):
    """Retrieve a remote ASPECT log, save it locally, then analyze it."""

    os.makedirs("remote_logs", exist_ok=True)

    local_log_path = os.path.join("remote_logs", "remote_log.txt")

    print("Connecting to remote HPC cluster...")

    with SSHConnector() as connector:
        if not connector.check_connection():
            print("Error: SSH connection check failed.")
            sys.exit(1)

        print("✓ SSH connection successful")

        print(f"\n[1/5] Reading remote ASPECT log:")
        print(f"  - {remote_log_path}")

        reader = RemoteLogReader(connector)
        reader.save_remote_log_locally(remote_log_path, local_log_path)

        print(f"  - Saved remote log locally to: {local_log_path}")

    print("\n[2/5] Running local analysis on downloaded log...")
    run_local_monitor(local_log_path)

def main():
    parser = argparse.ArgumentParser(
        description="ASPECT HPC-AI Monitor"
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    local_parser = subparsers.add_parser(
        "local",
        help="Analyze a local ASPECT log file"
    )
    local_parser.add_argument(
        "log_file",
        help="Path to local ASPECT log file"
    )
    local_parser.add_argument(
        "--ai",
        action="store_true",
        help="Enable AI diagnosis"
    )

    remote_parser = subparsers.add_parser(
        "remote",
        help="Check remote HPC Slurm job status"
    )
    remote_parser.add_argument(
        "--job-id",
        help="Optional Slurm job ID to check",
        default=None
    )

    remote_log_parser = subparsers.add_parser(
        "remote-log",
        help="Download and analyze a remote ASPECT log file"
    )
    remote_log_parser.add_argument(
        "--path",
        required=True,
        help="Full remote path to ASPECT log file"
    )

    args = parser.parse_args()

    if args.mode == "local":
        run_local_monitor(args.log_file)

        if args.ai:
            diagnoser = AIDiagnoser()
            diagnosis = diagnoser.diagnose(
                log_summary="Local ASPECT log analyzed successfully.",
                issue_summary="Use parser and analyzer summary from the generated report."
            )
            print("\nAI Diagnosis:")
            print(diagnosis)

    elif args.mode == "remote":
        run_remote_monitor(args.job_id)
        if __name__ == "__main__":
    main()
