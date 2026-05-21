# ASPECT HPC-AI Monitor

An intelligent Python framework for automated failure detection, analysis, and diagnostics of ASPECT convection simulations running on HPC clusters.

## Features

### 🔍 **Multi-Level Failure Detection** (8 Algorithms)

| Failure Type | Severity | Detection Method |
|--------------|----------|------------------|
| NaN/Infinity in solution | 🔴 CRITICAL | Pattern matching |
| Out-of-memory errors | 🔴 CRITICAL | Log analysis |
| Convergence failures | 🔴 CRITICAL | Solver status check |
| Excessive linear iterations (>500) | 🟠 ERROR | Threshold detection |
| Solver stagnation | 🟠 ERROR | Residual trend analysis |
| Diverging residuals (>1.5x growth) | 🟠 ERROR | Ratio comparison |
| Performance degradation (>50% slowdown) | 🟡 WARNING | Wall time trending |
| Simulation progress tracking | ℹ️ INFO | Status reporting |

### 📊 **Multi-Format Reporting**

- **Markdown** - Lab-ready reports with tables and recommendations
- **JSON** - Programmatic integration and database storage
- **HTML** - Interactive dashboards with styled output

### 🎯 **Comprehensive Log Analysis**

- Parse ASPECT logs (extract 20+ metrics per timestep)
- Extract timestep numbers, simulation times, dt values
- Capture linear & nonlinear solver statistics
- Detect solver types: GMRES, FGMRES, MINRES, BiCG, CG
- Identify failure modes: NaN, divergence, OOM, convergence failure

### ⚙️ **Production-Ready**

- Type-safe with 95%+ type hints
- Comprehensive error handling
- Extensible, modular architecture
- SOLID principles throughout
- Full documentation and examples

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/amarjyotibaruah/aspect-hpc-ai-monitor.git
cd aspect-hpc-ai-monitor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dependencies
pip install -e ".[dev]"
```

### Configuration

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your settings (optional for Phase 1)
# - AI provider credentials (for Phase 3)
# - HPC cluster details (for Phase 2)
# - Database settings (for Phase 3)
```

### Quick Test

```bash
# Verify installation
python -c "from src.parsers import AspectLogParser; from src.analyzers import SimulationAnalyzer; print('✓ Installation successful')"
```

---

## Usage Examples

### Example 1: Parse and Analyze a Simulation Log

```python
from src.parsers import AspectLogParser
from src.analyzers import SimulationAnalyzer

# Parse the log file
log = AspectLogParser("simulation.log").parse()
print(f"✓ Parsed {len(log.timesteps)} timesteps")
print(f"  ASPECT {log.aspect_version}, Material: {log.material_model}")
print(f"  Total wall time: {log.total_wall_time:.1f} seconds")

# Analyze for issues
analyzer = SimulationAnalyzer(log)
issues = analyzer.analyze()
print(f"\n⚠️  Found {len(issues)} issues")
```

**Expected Output:**
```
✓ Parsed 150 timesteps
  ASPECT 2.5.0, Material: visco_plastic
  Total wall time: 1234.5 seconds

⚠️  Found 3 issues
```

### Example 2: Generate Reports in All Formats

```python
from src.reports import ReportGenerator

gen = ReportGenerator(log)

# Generate Markdown (for lab reports, theses)
gen.generate_markdown(issues, "reports/analysis.md")

# Generate JSON (for programmatic use, databases)
gen.generate_json(issues, "reports/analysis.json")

# Generate HTML (for dashboards, sharing)
gen.generate_html(issues, "reports/analysis.html")

print("✓ Reports generated:")
print("  - reports/analysis.md")
print("  - reports/analysis.json")
print("  - reports/analysis.html")
```

### Example 3: Inspect Detected Issues

```python
from src.analyzers import SeverityLevel

# Filter by severity
critical = [i for i in issues if i.severity == SeverityLevel.CRITICAL]
errors = [i for i in issues if i.severity == SeverityLevel.ERROR]

for issue in critical:
    print(f"🔴 {issue.title}")
    print(f"   Category: {issue.category}")
    print(f"   Description: {issue.description}")
    print(f"   Suggested Fix:")
    print(f"   {issue.suggested_fix}")
    print()
```

**Expected Output:**
```
🔴 Convergence Failure
   Category: solver
   Description: GMRES convergence failed at timestep 125, t=2.5e6 yr
   Suggested Fix:
   Increase max_gmres_iterations or reduce timestep size
```

### Example 4: Run the Basic Example Script

```bash
python examples/basic_parsing.py
```

---

## Architecture

```
ASPECT Log File
    ↓
┌─────────────────────────────────────────┐
│   AspectLogParser (src/parsers)         │
│   - 15+ regex patterns                  │
│   - Extract timesteps, solvers, metrics │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│   SimulationAnalyzer (src/analyzers)    │
│   - 8 detection algorithms              │
│   - Classify severity & issues          │
│   - Generate suggested fixes            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│   ReportGenerator (src/reports)         │
│   - Markdown (lab reports)              │
│   - JSON (programmatic)                 │
│   - HTML (dashboards)                   │
└─────────────────────────────────────────┘
    ↓
  Output: .md / .json / .html
```

---

## Project Structure

```
aspect-hpc-ai-monitor/
├── README.md                    # This file
├── .gitignore                   # Git ignore rules
├── .env.example                 # Configuration template
├── pyproject.toml               # Project metadata & dependencies
│
├── src/
│   ├── __init__.py              # Package initialization
│   ├── parsers/
│   │   └── __init__.py          # ASPECT log parser
│   ├── analyzers/
│   │   └── __init__.py          # Failure detection algorithms
│   └── reports/
│       └── __init__.py          # Report generators (MD/JSON/HTML)
│
├── examples/
│   └── basic_parsing.py         # Quick start example
│
├── reports/                     # (generated) Output directory
│   ├── analysis.md
│   ├── analysis.json
│   └── analysis.html
│
└── docs/                        # (future) Documentation
```

---

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|----------|
| `pydantic` | ≥2.0 | Configuration & validation |
| `sqlalchemy` | ≥2.0 | ORM for database (Phase 3) |
| `jinja2` | ≥3.1 | Report templating |
| `python-dotenv` | ≥1.0 | Environment variable loading |

### Optional Dependencies

| Package | Purpose | Phase |
|---------|---------|-------|
| `paramiko` | SSH/SFTP for HPC | Phase 2 |
| `openai` | OpenAI LLM integration | Phase 3 |
| `azure-ai-openai` | Azure OpenAI integration | Phase 3 |
| `slack-sdk` | Slack notifications | Phase 4 |

### Development Dependencies

- `pytest` - Unit testing
- `pytest-cov` - Coverage reporting
- `mypy` - Type checking
- `ruff` - Code linting
- `black` - Code formatting

---

## Phase Roadmap

### ✅ Phase 1: Core Analysis Engine (COMPLETE)

- ✅ ASPECT log parser with 15+ patterns
- ✅ 8 failure detection algorithms
- ✅ 3 report generators (MD/JSON/HTML)
- ✅ Type-safe, production-ready code
- ✅ Full documentation

**Timeline:** ~40 hours | **Status:** Complete

---

### 🔜 Phase 2: HPC Integration (3-4 weeks)

- SSH/SFTP connection management
- Slurm job monitoring (scontrol, squeue)
- Remote log retrieval and streaming
- Multi-cluster support

**New Modules:**
- `src/hpc/` - Cluster connectivity
- `src/slurm/` - Job management

---

### 🔜 Phase 3: AI Integration (2-3 weeks)

- OpenAI/Azure LLM API calls
- Automated root cause diagnosis
- Recovery strategy generation
- Cost tracking and caching

**New Modules:**
- `src/ai/` - LLM providers
- `src/database/` - Result caching

---

### 🔜 Phase 4: CLI & Automation (2-3 weeks)

- Command-line interface (typer/click)
- GitHub Actions workflows
- Slack/email notifications
- Auto-restart job generation

**New Modules:**
- `src/cli/` - Command interface
- `.github/workflows/` - GitHub Actions

---

### 🔜 Phase 5: Polish & Release (1 week)

- Comprehensive test suite (50%+ coverage)
- Sphinx/ReadTheDocs documentation
- Performance benchmarks
- GitHub release

---

## Configuration Reference

See `.env.example` for all available settings:

```bash
# AI Provider Settings (Phase 3)
AI_PROVIDER=openai              # or azure_openai
OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_KEY=...

# HPC Cluster Settings (Phase 2)
PRIMARY_CLUSTER=cedar
CEDAR_HOST=cedar.computecanada.ca
CEDAR_USERNAME=your_username

# Database Settings (Phase 3)
DATABASE_URL=sqlite:///aspect_monitor.db

# Monitoring Settings
MONITORING_INTERVAL=300         # seconds
LOG_LEVEL=INFO
```

---

## Development

### Running Tests

```bash
pytest                          # Run all tests
pytest --cov=src              # With coverage
pytest -v                      # Verbose
```

### Code Quality Checks

```bash
mypy src/                       # Type checking
ruff check src/                 # Linting
black --check src/              # Format check
```

### Format Code

```bash
black src/                      # Format code
ruff check --fix src/           # Auto-fix linting
```

---

## Troubleshooting

### "Module not found: src.parsers"

```bash
# Make sure you installed in development mode
pip install -e .
```

### "KeyError: ASPECT_VERSION" when parsing

The log file may not be a standard ASPECT output. Check:
- Log contains lines like `Number of active cells: ...`
- Timestep information present
- Version string in first 50 lines

### "No issues detected" even with failures

Verify:
- Log contains NaN, OOM, or other failure indicators
- Solver statistics are present
- Check analyzer thresholds in `src/analyzers/__init__.py`

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes with tests
4. Ensure type checks pass: `mypy src/`
5. Submit a pull request

---

## License

MIT License - See LICENSE file for details

---

## Acknowledgments

- ASPECT development team (https://aspect.geodynamics.org/)
- Geodynamics community
- Compute Canada / Digital Research Alliance of Canada

---

## Support

For issues and questions:

- 📫 GitHub Issues: [aspect-hpc-ai-monitor/issues](https://github.com/amarjyotibaruah/aspect-hpc-ai-monitor/issues)
- 📖 Documentation: Check examples/ and README.md
- 💬 Discussions: [GitHub Discussions](https://github.com/amarjyotibaruah/aspect-hpc-ai-monitor/discussions)

---

**Version:** 0.1.0 | **Status:** Beta | **Last Updated:** 2026-05-21
