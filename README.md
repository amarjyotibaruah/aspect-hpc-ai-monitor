# aspect-hpc-ai-monitor

AI-assisted monitoring and automation framework for ASPECT geodynamic simulations on HPC clusters.

---

## Overview

`aspect-hpc-ai-monitor` is a Python-based workflow tool designed to automate the monitoring, analysis, and reporting of large-scale ASPECT geodynamic simulations running on HPC systems such as:

- Cedar
- Fir
- Graham
- Béluga
- Niagara

The framework parses ASPECT log files, detects numerical issues, analyzes solver behavior, monitors Slurm jobs remotely, and generates automated reports for simulation diagnostics.

---

## Features

### Local ASPECT Log Analysis
- Parse ASPECT `log.txt` files
- Extract timestep information
- Detect convergence issues
- Detect GMRES / FGMRES failures
- Detect NaN occurrences
- Detect memory-related issues
- Generate automated Markdown reports

### Remote HPC Monitoring
- SSH connection to HPC clusters
- Slurm job monitoring
- Active job inspection
- Recent job history tracking
- Individual job status checking

### Planned Features
- AI-generated simulation diagnostics
- Automated recovery suggestions
- PDF report generation
- Email notifications
- Daily scheduled monitoring
- Automatic remote log retrieval
- Interactive dashboard

---

# Project Structure

```text
aspect-hpc-ai-monitor/
├── monitor.py
├── README.md
├── pyproject.toml
├── .env.example
├── examples/
│   └── sample_log.txt
├── reports/
├── src/
│   ├── analyzers/
│   ├── hpc/
│   ├── parsers/
│   └── reports/
