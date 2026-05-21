"""
Failure detection and analysis engine for ASPECT simulations.

Implements 8 multi-level detection algorithms to identify:
  1. NaN/Divergence (CRITICAL)
  2. Out-of-memory errors (CRITICAL)
  3. Convergence failures (CRITICAL)
  4. Excessive linear iterations (ERROR)
  5. Solver stagnation (ERROR)
  6. Residual divergence (ERROR)
  7. Performance degradation (WARNING)
  8. Simulation status tracking (INFO)

Main Classes:
  - SimulationAnalyzer: Main analysis engine
  - Issue: Detected problem record
  - SeverityLevel: Enum for severity
  - DiagnosticReport: Analysis result

Usage:
    analyzer = SimulationAnalyzer(log)
    issues = analyzer.analyze()
    for issue in issues:
        print(f"{issue.severity}: {issue.title}")
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from src.parsers import AspectLog, SolverType, TimestepInfo


class SeverityLevel(str, Enum):
    """Issue severity classification."""

    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """A detected issue in the simulation."""

    severity: SeverityLevel
    category: str  # e.g., 'solver', 'memory', 'numerical', 'performance'
    title: str
    description: str
    timestep: Optional[int] = None
    suggested_fix: str = ""
    metrics: dict = field(default_factory=dict)


@dataclass
class DiagnosticReport:
    """Complete analysis report."""

    issues: list[Issue] = field(default_factory=list)
    total_timesteps: int = 0
    failed_timesteps: int = 0
    critical_count: int = 0
    error_count: int = 0
    warning_count: int = 0


class SimulationAnalyzer:
    """Analyzes parsed ASPECT logs for failures and anomalies."""

    # Configurable thresholds
    GMRES_ITERATION_THRESHOLD = 500
    EXCESSIVE_ITERATION_THRESHOLD = 1000
    RESIDUAL_ERROR_THRESHOLD = 1e-2
    RESIDUAL_WARNING_THRESHOLD = 1e-3
    RESIDUAL_DIVERGENCE_RATIO = 1.5  # 50% growth
    WALL_TIME_DEGRADATION_THRESHOLD = 1.5  # 50% increase

    def __init__(self, log: AspectLog):
        """
        Initialize analyzer.

        Args:
            log: AspectLog object from parser
        """
        self.log = log
        self.issues: list[Issue] = []

    def analyze(self) -> list[Issue]:
        """
        Run all detection algorithms.

        Returns:
            List of detected issues
        """
        self.issues = []

        # Run all detectors
        self._detect_nan_divergence()
        self._detect_oom_errors()
        self._detect_convergence_failures()
        self._detect_excessive_iterations()
        self._detect_solver_stagnation()
        self._detect_residual_divergence()
        self._detect_performance_degradation()
        self._report_simulation_status()

        return self.issues

    def _detect_nan_divergence(self) -> None:
        """Algorithm 1: Detect NaN/Infinity in solution (CRITICAL)."""
        if self.log.has_global_nan:
            self.issues.append(
                Issue(
                    severity=SeverityLevel.CRITICAL,
                    category="numerical",
                    title="NaN/Divergence Detected",
                    description="NaN or Infinity detected in simulation solution.",
                    suggested_fix=(
                        "1. Reduce timestep size\n"
                        "2. Increase solver tolerances\n"
                        "3. Check material properties for extreme values\n"
                        "4. Verify boundary conditions"
                    ),
                    metrics={"global_nan": True},
                )
            )

        # Check per-timestep
        for ts in self.log.timesteps:
            if ts.has_nan:
                self.issues.append(
                    Issue(
                        severity=SeverityLevel.CRITICAL,
                        category="numerical",
                        title="NaN Detected in Timestep",
                        description=f"NaN detected at timestep {ts.number}, t={ts.time:.2e} yr",
                        timestep=ts.number,
                        suggested_fix="Reduce timestep size and restart from last successful checkpoint",
                        metrics={"timestep": ts.number, "time": ts.time},
                    )
                )

    def _detect_oom_errors(self) -> None:
        """Algorithm 2: Detect out-of-memory errors (CRITICAL)."""
        if self.log.has_oom_error:
            self.issues.append(
                Issue(
                    severity=SeverityLevel.CRITICAL,
                    category="memory",
                    title="Out-of-Memory Error",
                    description="Job killed due to memory limit exceeded.",
                    suggested_fix=(
                        "1. Use coarser mesh or fewer elements\n"
                        "2. Increase memory allocation in job script\n"
                        "3. Request more compute nodes\n"
                        "4. Reduce number of particles for particle advection"
                    ),
                    metrics={"oom_detected": True},
                )
            )

    def _detect_convergence_failures(self) -> None:
        """Algorithm 3: Detect solver convergence failures (CRITICAL)."""
        for ts in self.log.timesteps:
            if ts.failure_type == "Convergence failure":
                self.issues.append(
                    Issue(
                        severity=SeverityLevel.CRITICAL,
                        category="solver",
                        title="Convergence Failure",
                        description=(
                            f"Linear or nonlinear solver failed to converge at "
                            f"timestep {ts.number}, t={ts.time:.2e} yr"
                        ),
                        timestep=ts.number,
                        suggested_fix=(
                            "1. Increase max_gmres_iterations\n"
                            "2. Reduce timestep size\n"
                            "3. Improve preconditioner settings\n"
                            "4. Check for ill-conditioned system"
                        ),
                        metrics={"timestep": ts.number, "time": ts.time},
                    )
                )

    def _detect_excessive_iterations(self) -> None:
        """Algorithm 4: Detect excessive linear iterations (ERROR/CRITICAL)."""
        for ts in self.log.timesteps:
            max_iters = ts.max_linear_iterations
            avg_iters = ts.avg_linear_iterations

            if max_iters > self.EXCESSIVE_ITERATION_THRESHOLD:
                severity = SeverityLevel.CRITICAL
            elif max_iters > self.GMRES_ITERATION_THRESHOLD:
                severity = SeverityLevel.ERROR
            else:
                continue

            self.issues.append(
                Issue(
                    severity=severity,
                    category="solver",
                    title="Excessive Linear Iterations",
                    description=(
                        f"Linear solver at timestep {ts.number} required "
                        f"{max_iters} iterations (threshold: {self.GMRES_ITERATION_THRESHOLD})"
                    ),
                    timestep=ts.number,
                    suggested_fix=(
                        "1. Improve preconditioner (e.g., ilu instead of jacobi)\n"
                        "2. Reduce timestep size\n"
                        "3. Increase max GMRES iterations to handle harder systems\n"
                        "4. Check mesh quality and refinement"
                    ),
                    metrics={
                        "timestep": ts.number,
                        "max_iterations": max_iters,
                        "avg_iterations": round(avg_iters, 1),
                    },
                )
            )

    def _detect_solver_stagnation(self) -> None:
        """Algorithm 5: Detect solver stagnation (ERROR)."""
        for ts in self.log.timesteps:
            if not ts.linear_solvers or len(ts.linear_solvers) < 2:
                continue

            # Check if residual is not decreasing
            solvers = ts.linear_solvers
            for i in range(1, len(solvers)):
                prev_residual = solvers[i - 1].residual
                curr_residual = solvers[i].residual

                if prev_residual > 0 and curr_residual > prev_residual * 0.95:
                    self.issues.append(
                        Issue(
                            severity=SeverityLevel.ERROR,
                            category="solver",
                            title="Solver Stagnation",
                            description=(
                                f"Residual not decreasing at timestep {ts.number}: "
                                f"{solvers[i-1].solver_type.value} residual {prev_residual:.2e} -> "
                                f"{solvers[i].solver_type.value} {curr_residual:.2e}"
                            ),
                            timestep=ts.number,
                            suggested_fix=(
                                "1. Improve preconditioner quality\n"
                                "2. Check matrix conditioning\n"
                                "3. Reduce timestep size\n"
                                "4. Verify boundary conditions"
                            ),
                            metrics={
                                "timestep": ts.number,
                                "prev_residual": f"{prev_residual:.2e}",
                                "curr_residual": f"{curr_residual:.2e}",
                            },
                        )
                    )

    def _detect_residual_divergence(self) -> None:
        """Algorithm 6: Detect diverging residuals (ERROR)."""
        for ts in self.log.timesteps:
            if not ts.linear_solvers:
                continue

            for solver in ts.linear_solvers:
                if solver.residual > self.RESIDUAL_ERROR_THRESHOLD:
                    self.issues.append(
                        Issue(
                            severity=SeverityLevel.ERROR,
                            category="numerical",
                            title="High Residual Value",
                            description=(
                                f"Final residual {solver.residual:.2e} exceeds "
                                f"threshold {self.RESIDUAL_ERROR_THRESHOLD:.2e} at "
                                f"timestep {ts.number}"
                            ),
                            timestep=ts.number,
                            suggested_fix=(
                                "1. Check convergence criteria\n"
                                "2. Improve preconditioner\n"
                                "3. Increase solver iterations\n"
                                "4. Investigate ill-conditioned system"
                            ),
                            metrics={
                                "timestep": ts.number,
                                "residual": f"{solver.residual:.2e}",
                                "threshold": f"{self.RESIDUAL_ERROR_THRESHOLD:.2e}",
                            },
                        )
                    )

    def _detect_performance_degradation(self) -> None:
        """Algorithm 7: Detect performance degradation (WARNING)."""
        if len(self.log.timesteps) < 10:
            return

        early_times = [ts.wall_time_seconds for ts in self.log.timesteps[:5]]
        late_times = [ts.wall_time_seconds for ts in self.log.timesteps[-5:]]

        early_avg = sum(early_times) / len(early_times)
        late_avg = sum(late_times) / len(late_times)

        if early_avg > 0 and late_avg / early_avg > self.WALL_TIME_DEGRADATION_THRESHOLD:
            degradation_pct = (late_avg / early_avg - 1) * 100
            self.issues.append(
                Issue(
                    severity=SeverityLevel.WARNING,
                    category="performance",
                    title="Performance Degradation",
                    description=(
                        f"Significant slowdown detected: "
                        f"early {early_avg:.2f}s/ts -> late {late_avg:.2f}s/ts (+{degradation_pct:.1f}%)"
                    ),
                    suggested_fix=(
                        "1. Check for load imbalance across MPI ranks\n"
                        "2. Monitor system resource usage\n"
                        "3. Verify mesh adaptation isn't over-refining\n"
                        "4. Check I/O and checkpoint overhead"
                    ),
                    metrics={
                        "early_avg_s": round(early_avg, 2),
                        "late_avg_s": round(late_avg, 2),
                        "degradation_pct": round(degradation_pct, 1),
                    },
                )
            )

    def _report_simulation_status(self) -> None:
        """Algorithm 8: Report simulation status (INFO)."""
        total = len(self.log.timesteps)
        failed = len(self.log.failed_timesteps)
        completed = total - failed
        pct_complete = (completed / total * 100) if total > 0 else 0

        self.issues.append(
            Issue(
                severity=SeverityLevel.INFO,
                category="status",
                title="Simulation Status",
                description=(
                    f"Simulation completed {completed}/{total} timesteps ({pct_complete:.1f}%), "
                    f"wall time {self.log.total_wall_time:.1f}s, "
                    f"avg {self.log.avg_wall_time_per_timestep:.2f}s/ts"
                ),
                metrics={
                    "total_timesteps": total,
                    "completed_timesteps": completed,
                    "failed_timesteps": failed,
                    "completion_pct": round(pct_complete, 1),
                    "total_wall_time_s": round(self.log.total_wall_time, 1),
                    "avg_time_per_ts_s": round(self.log.avg_wall_time_per_timestep, 2),
                },
            )
        )
