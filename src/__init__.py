"""
ASPECT HPC-AI Monitor

Intelligent framework for automated failure detection, analysis, and diagnostics
of ASPECT convection simulations running on HPC clusters.

Version: 0.1.0
Phase: 1 (Core Analysis Engine)

Modules:
  - parsers: ASPECT log file parsing with 15+ regex patterns
  - analyzers: 8-algorithm failure detection system
  - reports: Multi-format report generation (MD/JSON/HTML)

Quick Start:
    from src.parsers import AspectLogParser
    from src.analyzers import SimulationAnalyzer
    from src.reports import ReportGenerator

    log = AspectLogParser("simulation.log").parse()
    issues = SimulationAnalyzer(log).analyze()
    gen = ReportGenerator(log)
    gen.generate_markdown(issues, "report.md")
"""

__version__ = "0.1.0"
__phase__ = "Phase 1: Core Analysis Engine"
__author__ = "Amarjyoti Baruah"
__license__ = "MIT"

__all__ = ["parsers", "analyzers", "reports"]
