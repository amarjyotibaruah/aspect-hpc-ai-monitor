"""Read ASPECT log files from a remote HPC cluster."""

class RemoteLogReader:
    """Retrieve remote ASPECT log content using SSHConnector."""

    def __init__(self, connector):
        self.connector = connector

    def read_remote_log(self, remote_log_path):
        """Read a remote log file using cat."""
        command = f"cat {remote_log_path}"
        stdout, stderr, code = self.connector.execute_command(command)

        if code != 0:
            raise RuntimeError(f"Failed to read remote log: {stderr}")

        return stdout

    def save_remote_log_locally(self, remote_log_path, local_log_path):
        """Download remote log content and save it locally."""
        log_content = self.read_remote_log(remote_log_path)

        with open(local_log_path, "w") as f:
            f.write(log_content)

        return local_log_path
