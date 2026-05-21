"""
ASPECT log file parser with comprehensive failure detection.

Extracts timestep information, solver statistics, and failure modes from
ASPECT simulation output logs using 15+ regex patterns.

Main Classes:
  - AspectLogParser: Main parser class
  - AspectLog: Parsed log structure
  - TimestepInfo: Per-timestep data
  - SolverStatistics: Linear solver metrics
  - SolverType: Enum of supported solvers

Usage:
    parser = AspectLogParser("simulation.log")
    log = parser.parse()
    print(f"Parsed {len(log.timesteps)} timesteps")
    print(f"Failed: {len(log.failed_timesteps)}")
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class SolverType(str, Enum):
    """Linear solver types found in ASPECT logs."""

    GMRES = "GMRES"
    FGMRES = "FGMRES"
    MINRES = "MINRES"
    CG = "CG"
    BICG = "BiCG"
    UNKNOWN = "Unknown"


@dataclass
class SolverStatistics:
    """Statistics for a single linear solver iteration."""

    solver_type: SolverType
    iterations: int
    residual: float
    iteration_target: float
    converged: bool = True


@dataclass
class NonlinearIteration:
    """Statistics for a single nonlinear iteration."""

    iteration_number: int
    residual: float
    linear_iterations: int


@dataclass
class TimestepInfo:
    """Information about a single timestep."""

    number: int
    time: float  # Simulation time in years
    time_step_size: float  # dt in years
    wall_time_seconds: float  # Wall clock time for this timestep
    nonlinear_iterations: list[NonlinearIteration] = field(default_factory=list)
    linear_solvers: list[SolverStatistics] = field(default_factory=list)
    has_nan: bool = False
    has_divergence: bool = False
    failed: bool = False
    failure_type: Optional[str] = None

    @property
    def avg_linear_iterations(self) -> float:
        """Average iterations across all linear solves."""
        if not self.linear_solvers:
            return 0.0
        return sum(s.iterations for s in self.linear_solvers) / len(self.linear_solvers)

    @property
    def max_linear_iterations(self) -> int:
        """Maximum iterations in any linear solve."""
        if not self.linear_solvers:
            return 0
        return max(s.iterations for s in self.linear_solvers)


@dataclass
class AspectLog:
    """Complete parsed ASPECT simulation log."""

    aspect_version: str
    material_model: str
    timesteps: list[TimestepInfo] = field(default_factory=list)
    has_global_nan: bool = False
    has_oom_error: bool = False

    @property
    def failed_timesteps(self) -> list[TimestepInfo]:
        """Return list of failed timesteps."""
        return [ts for ts in self.timesteps if ts.failed]

    @property
    def total_wall_time(self) -> float:
        """Total wall clock time in seconds."""
        return sum(ts.wall_time_seconds for ts in self.timesteps)

    @property
    def avg_wall_time_per_timestep(self) -> float:
        """Average wall time per timestep."""
        if not self.timesteps:
            return 0.0
        return self.total_wall_time / len(self.timesteps)


class AspectLogParser:
    """Parser for ASPECT simulation output logs."""

    # Regex patterns for parsing
    PATTERNS = {
        "version": re.compile(r"ASPECT version ([\d.]+)"),
        "material_model": re.compile(r"Material model: ([^\n]+)"),
        "timestep_num": re.compile(r"Timestep (\d+)"),
        "simulation_time": re.compile(r"Number of active cells: .*?Time step: (\d+\.?\d*)\s*s"),
        "time_years": re.compile(r"(\d+\.?\d*)[eE]([-+]?\d+)\s*yr"),
        "dt_value": re.compile(r"dt\s*=\s*(\d+\.?\d*)[eE]([-+]?\d+)\s*yr"),
        "wall_time": re.compile(r"Wall time:.*?(\d+\.\d+)\s*s"),
        "gmres_iterations": re.compile(r"GMRES.*?\b(\d+)\b.*?iterations"),
        "fgmres_iterations": re.compile(r"FGMRES.*?\b(\d+)\b.*?iterations"),
        "minres_iterations": re.compile(r"MINRES.*?\b(\d+)\b.*?iterations"),
        "residual": re.compile(r"Residual: ([\d.eE+-]+)"),
        "nan_detected": re.compile(r"[Nn][Aa][Nn]|NaN|[Ii]nfinity|[Ii]nf"),
        "convergence_failed": re.compile(r"[Cc]onvergence.*[Ff]ailed|[Ff]ailed.*[Cc]onvergence"),
        "divergence": re.compile(r"[Dd]iverg"),
        "oom_error": re.compile(r"[Oo]ut of [Mm]emory|OOM|[Mm]alloc.*[Ff]ailed"),
    }

    def __init__(self, log_file: str | Path, strict: bool = False):
        """
        Initialize parser.

        Args:
            log_file: Path to ASPECT log file
            strict: If True, raise on parsing errors; if False, skip gracefully
        """
        self.log_file = Path(log_file)
        self.strict = strict
        self.content = ""

    def parse(self) -> AspectLog:
        """
        Parse ASPECT log file.

        Returns:
            AspectLog object with all extracted data

        Raises:
            FileNotFoundError: If log file doesn't exist
            ValueError: If parsing fails and strict=True
        """
        if not self.log_file.exists():
            raise FileNotFoundError(f"Log file not found: {self.log_file}")

        with open(self.log_file, "r", errors="ignore") as f:
            self.content = f.read()

        # Extract basic info
        version = self._extract_version()
        material = self._extract_material_model()

        # Extract timestep information
        timesteps = self._extract_timesteps()

        # Detect global failures
        has_nan = bool(self.PATTERNS["nan_detected"].search(self.content))
        has_oom = bool(self.PATTERNS["oom_error"].search(self.content))

        log = AspectLog(
            aspect_version=version,
            material_model=material,
            timesteps=timesteps,
            has_global_nan=has_nan,
            has_oom_error=has_oom,
        )

        return log

    def _extract_version(self) -> str:
        """Extract ASPECT version."""
        match = self.PATTERNS["version"].search(self.content)
        if match:
            return match.group(1)
        return "Unknown"

    def _extract_material_model(self) -> str:
        """Extract material model name."""
        match = self.PATTERNS["material_model"].search(self.content)
        if match:
            return match.group(1).strip()
        return "Unknown"

    def _extract_timesteps(self) -> list[TimestepInfo]:
        """Extract all timesteps from log."""
        timesteps = []
        lines = self.content.split("\n")

        current_ts: Optional[TimestepInfo] = None
        ts_number = 0
        ts_time = 0.0
        ts_dt = 0.0
        ts_wall_time = 0.0

        for i, line in enumerate(lines):
            # Detect timestep start
            if "Timestep" in line and "active cells" in line:
                if current_ts:
                    timesteps.append(current_ts)

                ts_number += 1
                ts_time = self._extract_float_from_line(line, "time")
                ts_dt = self._extract_float_from_line(line, "dt")
                ts_wall_time = self._extract_float_from_line(line, "wall")

                current_ts = TimestepInfo(
                    number=ts_number,
                    time=ts_time,
                    time_step_size=ts_dt,
                    wall_time_seconds=ts_wall_time,
                )

            # Extract solver statistics
            if current_ts:
                self._extract_solver_stats(line, current_ts)
                self._check_failure_mode(line, current_ts)

        if current_ts:
            timesteps.append(current_ts)

        return timesteps

    def _extract_float_from_line(self, line: str, field_type: str) -> float:
        """Extract float value from a log line."""
        if field_type == "time":
            patterns = [r"t=([\d.eE+-]+)", r"time\s*=\s*([\d.eE+-]+)"]
        elif field_type == "dt":
            patterns = [r"dt\s*=\s*([\d.eE+-]+)", r"step\s*=\s*([\d.eE+-]+)"]
        elif field_type == "wall":
            patterns = [r"([\d.]+)\s*s", r"wall.*?([\d.]+)"]
        else:
            return 0.0

        for pattern in patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue

        return 0.0

    def _extract_solver_stats(self, line: str, timestep: TimestepInfo) -> None:
        """Extract solver statistics from a line."""
        solver_types = [
            ("gmres_iterations", SolverType.GMRES),
            ("fgmres_iterations", SolverType.FGMRES),
            ("minres_iterations", SolverType.MINRES),
        ]

        for pattern_key, solver_type in solver_types:
            match = self.PATTERNS[pattern_key].search(line)
            if match:
                iterations = int(match.group(1))
                residual_match = self.PATTERNS["residual"].search(line)
                residual = float(residual_match.group(1)) if residual_match else 0.0

                stats = SolverStatistics(
                    solver_type=solver_type,
                    iterations=iterations,
                    residual=residual,
                    iteration_target=1e-6,
                    converged=residual < 1e-2,
                )
                timestep.linear_solvers.append(stats)

    def _check_failure_mode(self, line: str, timestep: TimestepInfo) -> None:
        """Check line for failure indicators."""
        if self.PATTERNS["nan_detected"].search(line):
            timestep.has_nan = True
            timestep.failed = True
            timestep.failure_type = "NaN detected"

        if self.PATTERNS["convergence_failed"].search(line):
            timestep.failed = True
            timestep.failure_type = "Convergence failure"

        if self.PATTERNS["divergence"].search(line):
            timestep.has_divergence = True
            timestep.failed = True
            timestep.failure_type = "Divergence detected"
