# ASPECT HPC-AI Monitor

AI-assisted monitoring and diagnostic framework for ASPECT geodynamic simulations running on HPC clusters.

<img width="1536" height="1024" alt="ChatGPT Image May 26, 2026, 02_12_43 PM" src="https://github.com/user-attachments/assets/61865871-993f-49cc-8087-df4a57a713f7" />


---

# Overview

ASPECT HPC-AI Monitor is a Python-based workflow designed to:

- Monitor ASPECT simulation logs
- Analyze solver performance
- Detect convergence and runtime issues
- Retrieve logs directly from remote HPC clusters
- Generate automated Markdown reports
- Use OpenAI-powered AI diagnostics
- Send automated email reports
- Support scheduled daily monitoring workflows

This framework was developed for large-scale mantle convection and geodynamic simulations using ASPECT on Compute Canada / Digital Alliance HPC systems.

---

# Workflow Overview

```text
ASPECT Simulation
        ↓
Generate log.txt
        ↓
Local or Remote Retrieval
        ↓
Python Log Parsing
        ↓
Simulation Analysis
        ↓
AI Diagnosis (OpenAI API)
        ↓
Markdown Report Generation
        ↓
Automated Email Delivery
```

---

# Features

## Local Log Monitoring

Analyze local ASPECT log files directly.

### Command

```bash
python3 monitor.py local examples/sample_log.txt
```

### Output

- Solver statistics
- Error detection
- Timestep tracking
- Markdown report generation

---

## AI-Assisted Diagnostics

Use OpenAI models to analyze solver behavior and recommend fixes.

### Command

```bash
python3 monitor.py local examples/sample_log.txt --ai
```

### AI Capabilities

- FGMRES divergence analysis
- Nonlinear solver interpretation
- Timestep stability recommendations
- Solver tuning suggestions
- Memory issue interpretation
- Stability diagnostics

---

## Remote HPC Monitoring

Connect to remote HPC systems using SSH.

### Command

```bash
python3 monitor.py remote
```

### Features

- Slurm queue monitoring
- Recent job history analysis
- Remote cluster status inspection
- SSH-based workflow automation

---

## Remote Log Retrieval + AI Analysis

Automatically download and analyze remote ASPECT logs.

### Command

```bash
python3 monitor.py remote-log \
--path /path/to/log.txt \
--ai
```

### Workflow

```text
Remote HPC Cluster
        ↓
SSH Connection
        ↓
Retrieve ASPECT log
        ↓
Local Parsing & Analysis
        ↓
AI Diagnosis
        ↓
Markdown Report
```

---

## Automated Email Reporting

Automatically email AI-generated reports.

### Command

```bash
python3 monitor.py local examples/sample_log.txt --ai --email
```

### Email Features

- Markdown report attachment
- AI-generated diagnostics
- Automated delivery
- Gmail SMTP integration

---

## Daily Automated Monitoring

Supports scheduled automated monitoring using cron.

### Example Workflow

```text
Daily Cron Job
        ↓
SSH into HPC Cluster
        ↓
Download latest log.txt
        ↓
Analyze simulation
        ↓
Generate AI diagnosis
        ↓
Create report
        ↓
Email report automatically
```

---

# Example AI Diagnosis

```text
FGMRES divergence detected
        ↓
AI analyzes solver behavior
        ↓
Suggest:
- reduce timestep
- increase nonlinear iterations
- modify viscosity averaging
- adjust solver tolerances
```

---

# Project Structure

```text
aspect-hpc-ai-monitor/
│
├── monitor.py
├── run_daily_monitor.sh
│
├── src/
│   ├── ai/
│   │   └── ai_diagnoser.py
│   │
│   ├── analyzers/
│   │
│   ├── hpc/
│   │   ├── remote_log_reader.py
│   │   ├── slurm_checker.py
│   │   └── ssh_connector.py
│   │
│   ├── notifications/
│   │   └── email_sender.py
│   │
│   ├── parsers/
│   │   └── aspect_log_parser.py
│   │
│   └── reports/
│       └── report_generator.py
│
├── examples/
│   └── sample_log.txt
│
├── reports/
├── remote_logs/
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/amarjyotibaruah/aspect-hpc-ai-monitor.git

cd aspect-hpc-ai-monitor
```

---

## Install Dependencies

```bash
pip install openai paramiko
```

---

# Environment Variables

## OpenAI API

```bash
export OPENAI_API_KEY="your_api_key"
```

---

## HPC SSH Access

```bash
export HPC_HOST=fir.computecanada.ca
export HPC_USERNAME=your_username
export HPC_SSH_KEY=$HOME/.ssh/id_ed25519
```

---

## Email Notifications

```bash
export EMAIL_USER="your_email@gmail.com"
export EMAIL_PASSWORD="your_gmail_app_password"
export EMAIL_TO="your_email@gmail.com"
```

---

# Running the Framework

---

## Local Analysis

```bash
python3 monitor.py local examples/sample_log.txt
```

---

## Local AI Analysis

```bash
python3 monitor.py local examples/sample_log.txt --ai
```

---

## Local AI + Email Workflow

```bash
python3 monitor.py local examples/sample_log.txt --ai --email
```

---

## Remote Slurm Monitoring

```bash
python3 monitor.py remote
```

---

## Remote Log AI Monitoring

```bash
python3 monitor.py remote-log \
--path /path/to/log.txt \
--ai
```

---

## Remote Log AI + Email Workflow

```bash
python3 monitor.py remote-log \
--path /path/to/log.txt \
--ai \
--email
```

---

# Automation Setup

Example cron scheduling:

```bash
0 9 * * * /path/to/run_daily_monitor.sh
```

---

# Supported Diagnostics

The framework currently detects:

- Nonlinear solver divergence
- FGMRES convergence problems
- Memory issues
- NaN occurrences
- Solver instability
- Slurm job failures
- Runtime anomalies
- Timestep instability

---

# AI-Assisted Solver Recommendations

The AI module can suggest:

- Solver tolerance changes
- Timestep adjustments
- Viscosity averaging modifications
- Nonlinear iteration tuning
- Mesh refinement considerations
- Stability improvements

---

# Example Research Applications

This framework is designed for:

- Mantle convection simulations
- Subduction modeling
- Lithosphere dynamics
- Thermochemical convection
- HPC geodynamics workflows
- ASPECT-based Earth science research

---

# Future Development

Planned future features:

- Automatic job restart
- Multi-log monitoring
- Solver residual visualization
- Slack / Discord notifications
- Web dashboard
- Trend analysis across simulations
- AI-assisted timestep optimization
- ParaView integration
- Autonomous HPC workflow orchestration

---

# Research Context

Developed for:

- Large-scale geodynamic modeling
- High-performance computing workflows
- AI-assisted simulation diagnostics
- Computational geophysics research

---

# Author

Amar Jyoti Baruah  
PhD Researcher  
Computational Geodynamics & HPC Modeling

---

# License

MIT License

---

# Acknowledgements

- ASPECT Geodynamics Community
- Compute Canada / Digital Alliance
- OpenAI API
- Python Open Source Ecosystem
