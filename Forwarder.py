 #!/usr/bin/env python3
import os
import json
import boto3
import time
import subprocess
from pathlib import Path

class GitHubLogForwarder:
    def __init__(self):
        self.cloudwatch = boto3.client('logs')
        self.current_workflow_id = None
        self.log_group = None
        
    def get_workflow_info(self):
        """Extract workflow information from environment or runner logs"""
        # Method 1: From environment variables (available during job execution)
        workflow_id = os.environ.get('GITHUB_RUN_ID')
        repository = os.environ.get('GITHUB_REPOSITORY', 'unknown')
        runner_name = os.environ.get('RUNNER_NAME', 'unknown')
        
        if workflow_id:
            return {
                'workflow_id': workflow_id,
                'repository': repository,
                'runner_name': runner_name,
                'log_group': f"/github-runners/{repository.replace('/', '-')}/{workflow_id}"
            }
        
        # Method 2: Parse from runner diagnostics logs
        return self.parse_from_logs()
    
    def parse_from_logs(self):
        """Parse workflow info from runner diagnostic logs"""
        try:
            log_dir = Path('/home/runner/_diag')
            if log_dir.exists():
                log_files = sorted(log_dir.glob('Runner_*.log'), key=os.path.getmtime, reverse=True)
                if log_files:
                    latest_log = log_files[0]
                    with open(latest_log, 'r') as f:
                        content = f.read()
                        # Extract workflow information from log content
                        # This is a simplified example - actual parsing would be more robust
                        if 'WorkflowJobRequestId:' in content:
                            lines = content.split('\n')
                            for line in lines:
                                if 'WorkflowJobRequestId:' in line:
                                    workflow_id = line.split(':')[-1].strip()
                                    return {
                                        'workflow_id': workflow_id,
                                        'repository': 'parsed-from-logs',
                                        'runner_name': os.environ.get('HOSTNAME', 'unknown'),
                                        'log_group': f"/github-runners/parsed/{workflow_id}"
                                    }
        except Exception as e:
            print(f"Error parsing logs: {e}")
        
        return None
    
    def ensure_log_group(self, log_group_name):
        """Create log group if it doesn't exist"""
        try:
            self.cloudwatch.describe_log_groups(logGroupNamePrefix=log_group_name)
        except self.cloudwatch.exceptions.ResourceNotFoundException:
            self.cloudwatch.create_log_group(logGroupName=log_group_name)
            self.cloudwatch.put_retention_policy(
                logGroupName=log_group_name,
                retentionInDays=7
            )
    
    def start_forwarding(self):
        """Main forwarding loop"""
        while True:
            workflow_info = self.get_workflow_info()
            
            if workflow_info and workflow_info['workflow_id'] != self.current_workflow_id:
                self.current_workflow_id = workflow_info['workflow_id']
                self.log_group = workflow_info['log_group']
                self.ensure_log_group(self.log_group)
                print(f"Forwarding logs for workflow {self.current_workflow_id} to {self.log_group}")
            
            # Forward logs if we have an active workflow
            if self.log_group:
                self.forward_logs()
            
            time.sleep(5)

if __name__ == "__main__":
    forwarder = GitHubLogForwarder()
    forwarder.start_forwarding()
