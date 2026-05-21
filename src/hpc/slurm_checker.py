from src.hpc.ssh_connector import SSHConnector


class SlurmChecker:
    """Check Slurm job status on remote HPC clusters."""

    def __init__(self, connector: SSHConnector):
        self.connector = connector

    def get_user_jobs(self, username):
        command = f"squeue -u {username}"
        stdout, stderr, code = self.connector.execute_command(command)

        if code != 0:
            return f"Error: {stderr}"

        return stdout

    def get_recent_jobs(self, username):
        command = f"sacct -u {username} --format=JobID,JobName,State,Elapsed"
        stdout, stderr, code = self.connector.execute_command(command)

        if code != 0:
            return f"Error: {stderr}"

        return stdout

    def check_job(self, job_id):
        command = f"sacct -j {job_id} --format=JobID,JobName,State,Elapsed"
        stdout, stderr, code = self.connector.execute_command(command)

        if code != 0:
            return f"Error: {stderr}"

        return stdout
