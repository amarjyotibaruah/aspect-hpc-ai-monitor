"""SimulationAnalyzer for analyzing ASPECT simulation results."""


class SimulationAnalyzer:
    """Analyzer for ASPECT simulation log data."""

    def __init__(self, parser):
        """Initialize the analyzer with a log parser.

        Args:
            parser: An AspectLogParser instance with loaded log data.
        """
        self.parser = parser
        self.analysis_results = {}

    def analyze(self):
        """Run all analysis checks on the log data.

        Returns:
            Dictionary with all analysis results.
        """
        if self.parser.log_data is None:
            self.parser.read_log()

        self.analysis_results = {
            'error_lines': self._find_error_lines(),
            'failed_lines': self._find_failed_lines(),
            'convergence_failures': self._find_convergence_failures(),
            'gmres_warnings': self._find_gmres_warnings(),
            'nan_occurrences': self._find_nan(),
            'out_of_memory': self._find_out_of_memory(),
            'timestep_count': self._count_timesteps()
        }
        return self.analysis_results

    def _find_error_lines(self):
        """Find all error lines in the log.

        Returns:
            List of error lines.
        """
        return [line.strip() for line in self.parser.log_data if 'error' in line.lower()]

    def _find_failed_lines(self):
        """Find all failed operation lines.

        Returns:
            List of failed lines.
        """
        return [line.strip() for line in self.parser.log_data if 'failed' in line.lower()]

    def _find_convergence_failures(self):
        """Find convergence failure messages.

        Returns:
            List of convergence failure lines.
        """
        keywords = ['convergence', 'divergence', 'failed to converge']
        return [line.strip() for line in self.parser.log_data
                if any(kw in line.lower() for kw in keywords)]

    def _find_gmres_warnings(self):
        """Find GMRES or FGMRES solver warnings.

        Returns:
            List of GMRES/FGMRES warning lines.
        """
        keywords = ['gmres', 'fgmres', 'solver']
        return [line.strip() for line in self.parser.log_data
                if any(kw in line.lower() for kw in keywords) and 'warning' in line.lower()]

    def _find_nan(self):
        """Find NaN (Not a Number) occurrences.

        Returns:
            List of lines containing NaN.
        """
        return [line.strip() for line in self.parser.log_data if 'nan' in line.lower()]

    def _find_out_of_memory(self):
        """Find out of memory error messages.

        Returns:
            List of out of memory error lines.
        """
        keywords = ['out of memory', 'memory', 'allocation failed']
        return [line.strip() for line in self.parser.log_data
                if any(kw in line.lower() for kw in keywords)]

    def _count_timesteps(self):
        """Count the total number of timesteps in the simulation.

        Returns:
            Integer count of timesteps.
        """
        timestep_lines = self.parser.find_timesteps()
        return len(timestep_lines)

    def get_summary(self):
        """Get a summary of the analysis results.

        Returns:
            Dictionary with summary statistics.
        """
        if not self.analysis_results:
            self.analyze()

        return {
            'total_errors': len(self.analysis_results['error_lines']),
            'total_failures': len(self.analysis_results['failed_lines']),
            'convergence_issues': len(self.analysis_results['convergence_failures']),
            'solver_warnings': len(self.analysis_results['gmres_warnings']),
            'nan_count': len(self.analysis_results['nan_occurrences']),
            'memory_issues': len(self.analysis_results['out_of_memory']),
            'timesteps_completed': self.analysis_results['timestep_count']
        }
