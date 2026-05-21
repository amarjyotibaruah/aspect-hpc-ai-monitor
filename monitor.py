"""Main monitoring workflow script for aspect-hpc-ai-monitor."""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parsers.aspect_log_parser import AspectLogParser
from analyzers.simulation_analyzer import SimulationAnalyzer
from reports.report_generator import ReportGenerator


def main():
    """Main workflow: parse, analyze, and generate report."""
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python monitor.py <log_file_path>")
        print("Example: python monitor.py simulation.log")
        sys.exit(1)

    log_file = sys.argv[1]

    # Check if log file exists
    if not os.path.exists(log_file):
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)

    print(f"Processing log file: {log_file}")

    # Step 1: Parse the log file
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

    # Step 2: Analyze the parsed data
    print("\n[2/4] Analyzing simulation data...")
    analyzer = SimulationAnalyzer(parser)
    analyzer.analyze()

    analyzer_summary = analyzer.get_summary()
    print(f"  - Total errors: {analyzer_summary['total_errors']}")
    print(f"  - Convergence issues: {analyzer_summary['convergence_issues']}")
    print(f"  - Memory issues: {analyzer_summary['memory_issues']}")
    print(f"  - NaN occurrences: {analyzer_summary['nan_count']}")

    # Step 3: Generate report
    print("\n[3/4] Generating report...")
    generator = ReportGenerator(parser, analyzer)
    markdown_report_path = generator.generate_markdown_report()
    print(f"  - Markdown report generated")

    # Step 4: Summary
    print("\n[4/4] Workflow complete")
    print(f"\n✓ Report saved to: {markdown_report_path}")


if __name__ == '__main__':
    main()
