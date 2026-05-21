"""SSH connector for remote HPC cluster access."""

import os
import paramiko
from paramiko import SSHClient, AutoAddPolicy


class SSHConnector:
    """SSH connector for executing commands on remote HPC clusters."""

    def __init__(self):
        """Initialize SSH connector from environment variables.

        Reads configuration from:
        - HPC_HOST: Remote cluster hostname
        - HPC_USERNAME: SSH username
        - HPC_SSH_KEY: Path to SSH private key file
        """
        self.host = os.getenv('HPC_HOST')
        self.username = os.getenv('HPC_USERNAME')
        self.ssh_key_path = os.getenv('HPC_SSH_KEY')
        self.client = None

        if not all([self.host, self.username, self.ssh_key_path]):
            raise ValueError(
                "Missing required environment variables: "
                "HPC_HOST, HPC_USERNAME, HPC_SSH_KEY"
            )

        if not os.path.exists(self.ssh_key_path):
            raise FileNotFoundError(
                f"SSH key not found: {self.ssh_key_path}"
            )

    def connect(self):
        """Establish SSH connection to the remote host.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            self.client = SSHClient()
            self.client.set_missing_host_key_policy(AutoAddPolicy())
            self.client.connect(
                self.host,
                username=self.username,
                key_filename=self.ssh_key_path,
                timeout=10
            )
            return True
        except paramiko.AuthenticationException:
            print(f"Authentication failed for {self.username}@{self.host}")
            return False
        except paramiko.SSHException as e:
            print(f"SSH error: {e}")
            return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False

    def disconnect(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            self.client = None

    def execute_command(self, command):
        """Execute a command on the remote host.

        Args:
            command: Command string to execute.

        Returns:
            tuple: (stdout, stderr, return_code) or (None, error_msg, -1) on error.
        """
        if not self.client:
            return None, "Not connected. Call connect() first.", -1

        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            stdout_data = stdout.read().decode('utf-8')
            stderr_data = stderr.read().decode('utf-8')
            return_code = stdout.channel.recv_exit_status()

            return stdout_data, stderr_data, return_code
        except Exception as e:
            return None, f"Command execution error: {e}", -1

    def check_connection(self):
        """Check SSH connection with a simple echo command.

        Returns:
            bool: True if connection is working, False otherwise.
        """
        stdout, stderr, return_code = self.execute_command('echo "SSH connection OK"')

        if return_code == 0 and stdout:
            return True
        return False

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
