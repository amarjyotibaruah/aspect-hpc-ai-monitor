#!/usr/bin/env python
"""
Basic example demonstrating Phase 1 functionality:
- Parse an ASPECT simulation log
- Analyze for failures
- Generate reports in all formats

Usage:
    python examples/basic_parsing.py
    python examples/basic_parsing.py --logfile /path/to/simulation.log

Or use in Python:
    from examples.basic_parsing import create_sample_log, run_analysis
    log_content = create_sample_log()
    run_analysis(log_content)
"""

import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.analyzers import SimulationAnalyzer, SeverityLevel
from src.parsers import AspectLogParser
from src.reports import ReportGenerator


def create_sample_log() -> str:
    """
    Create a sample ASPECT log for demonstration.

    Returns:
        Sample log content as string
    """
    return """===============================
ASPECT version 2.5.0
Material model: visco_plastic
===============================

Timestep 1: Number of active cells: 1024, Time step: 0.0 s, Time: 1.00e+05 yr, dt: 1.00e+04 yr
Wall time: 5.23 s
GMRES: 127 iterations, Residual: 8.45e-07
Nonlinear iteration 1: residual: 2.14e-03

Timestep 2: Number of active cells: 1256, Time step: 1.00e+04 s, Time: 1.10e+05 yr, dt: 1.00e+04 yr
Wall time: 6.15 s
GMRES: 145 iterations, Residual: 9.23e-07
Nonlinear iteration 1: residual: 1.87e-03

Timestep 3: Number of active cells: 1512, Time step: 2.00e+04 s, Time: 1.20e+05 yr, dt: 1.00e+04 yr
Wall time: 7.42 s
GMRES: 203 iterations, Residual: 5.14e-06  [High residual detected]
Nonlinear iteration 1: residual: 2.45e-03

Timestep 4: Number of active cells: 1024, Time step: 3.00e+04 s, Time: 1.30e+05 yr, dt: 1.00e+04 yr
Wall time: 8.91 s
GMRES: 687 iterations, Residual: 3.21e-06
Nonlinear iteration 1: residual: 1.92e-03

Timestep 5: Number of active cells: 1024, Time step: 4.00e+04 s, Time: 1.40e+05 yr, dt: 1.00e+04 yr
Wall time: 10.23 s
GMRES: 1250 iterations, Residual: 1.45e-03
Nonlinear iteration 1: residual: 2.01e-03
"""


def run_analysis(log_content: str, output_dir: str = "./reports") -> None:
    """
    Run complete analysis pipeline.

    Args:
        log_content: Log file content as string
        output_dir: Directory for output reports
    """
    # Create temporary log file
    with NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
        f.write(log_content)
        log_file = f.name

    try:
        print("="* 80)
        print("ASPECT HPC-AI Monitor - Phase 1 Example")
        print("="* 80)
        print()

        # Step 1: Parse
        print("[1/4] Parsing ASPECT log file...")
        parser = AspectLogParser(log_file)
        log = parser.parse()
        print(f"    ✓ Parsed {len(log.timesteps)} timesteps")
        print(f"    ✓ ASPECT {log.aspect_version}, {log.material_model}")
        print(f"    ✓ Total wall time: {log.total_wall_time:.1f} seconds")
        print()

        # Step 2: Analyze
        print("[2/4] Running failure detection algorithms...")
        analyzer = SimulationAnalyzer(log)
        issues = analyzer.analyze()
        print(f"    ✓ Found {len(issues)} issues:")
        for severity in [SeverityLevel.CRITICAL, SeverityLevel.ERROR, SeverityLevel.WARNING, SeverityLevel.INFO]:
            count = len([i for i in issues if i.severity == severity])
            if count > 0:
                emoji = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "ℹ️"}[severity.value]
                print(f"      {emoji} {severity.value.upper()}: {count}")
        print()

        # Step 3: Generate reports
        print("[3/4] Generating reports...")
        output_path = Path(output_dir)
        gen = ReportGenerator(log)

        # Markdown
        md_path = output_path / "analysis.md"
        gen.generate_markdown(issues, md_path)
        print(f"    ✓ Markdown: {md_path}")

        # JSON
        json_path = output_path / "analysis.json"
        gen.generate_json(issues, json_path)
        print(f"    ✓ JSON: {json_path}")

        # HTML
        html_path = output_path / "analysis.html"
        gen.generate_html(issues, html_path)
        print(f"    ✓ HTML: {html_path}")
        print()

        # Step 4: Display summary
        print("[4/4] Analysis Summary")
        print("-" * 80)

        for issue in issues:
            icon = {"critical": "🔴", "error": "🟠", "warning": "🟡", "info": "ℹ️"}[issue.severity.value]
            print(f"{icon} [{issue.category.upper()}] {issue.title}")
            if issue.timestep:
                print(f"   Timestep: {issue.timestep}")
            print(f"   {issue.description}")
            print()

        print("-" * 80)
        print()
        print(f"✅ Analysis complete!")
        print(f"   Reports available in: {output_path}")
        print(f"   Open {html_path} in a browser for interactive dashboard")
        print()

    finally:
        # Cleanup
        Path(log_file).unlink(missing_ok=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ASPECT HPC-AI Monitor - Phase 1 Example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Use sample log
  %(prog)s --logfile simulation.log           # Parse real ASPECT log
  %(prog)s --logfile sim.log --output /tmp    # Specify output directory
        """,
    )
    parser.add_argument(
        "--logfile",
        type=str,
        default=None,
        help="Path to ASPECT log file (default: use sample log)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="./reports",
        help="Output directory for reports (default: ./reports)",
    )

    args = parser.parse_args()

    if args.logfile:
        if not Path(args.logfile).exists():
            print(f"❌ Error: Log file not found: {args.logfile}")
            sys.exit(1)
        print(f"Loading log file: {args.logfile}")
        with open(args.logfile) as f:
            log_content = f.read()
    else:
        print("Using sample ASPECT log (5 timesteps)")
        log_content = create_sample_log()

    run_analysis(log_content, args.output)
