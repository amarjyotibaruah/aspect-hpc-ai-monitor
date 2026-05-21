"""AspectLogParser for parsing ASPECT log files."""


class AspectLogParser:
    """Parser for ASPECT HPC simulation log files."""

    def __init__(self, log_path):
        """Initialize the parser with a log file path.

        Args:
            log_path: Path to the ASPECT log file.
        """
        self.log_path = log_path
        self.log_data = None

    def read_log(self):
        """Read and load the log file.

        Returns:
            List of log lines.
        """
        try:
            with open(self.log_path, 'r') as f:
                self.log_data = f.readlines()
            return self.log_data
        except FileNotFoundError:
            print(f"Log file not found: {self.log_path}")
            return None

    def find_errors(self):
        """Find all error messages in the log.

        Returns:
            List of error lines.
        """
        if self.log_data is None:
            self.read_log()

        errors = [line for line in self.log_data if 'error' in line.lower()]
        return errors

    def find_timesteps(self):
        """Find all timestep information in the log.

        Returns:
            List of timestep lines.
        """
        if self.log_data is None:
            self.read_log()

        timesteps = [line for line in self.log_data if 'timestep' in line.lower()]
        return timesteps

    def summarize(self):
        """Generate a summary of the log file.

        Returns:
            Dictionary with summary statistics.
        """
        if self.log_data is None:
            self.read_log()

        summary = {
            'total_lines': len(self.log_data) if self.log_data else 0,
            'errors_count': len(self.find_errors()),
            'timesteps_count': len(self.find_timesteps())
        }
        return summary
