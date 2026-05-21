"""Main monitoring workflow script for aspect-hpc-ai-monitor."""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from parsers.aspect_log_parser import AspectLogParser
from analyzers.simulation_analyzer import SimulationAnalyzer
from reports.report_generator import ReportGenerator


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


def main():
    parser = argparse.ArgumentParser(
        description="ASPECT HPC-AI Monitor"
    )

    parser.add_argument(
        "mode",
        choices=["local"],
        help="Monitoring mode. Currently supported: local"
    )

    parser.add_argument(
        "log_file",
        help="Path to local ASPECT log file"
    )

    args = parser.parse_args()

    if args.mode == "local":
        run_local_monitor(args.log_file)


if __name__ == "__main__":
    main()
