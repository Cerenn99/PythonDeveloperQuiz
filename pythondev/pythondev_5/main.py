import paramiko
import asyncio
from fastapi import FastAPI, BackgroundTasks
from typing import List

app = FastAPI()

class SSHClientManager:
    def __init__(self, host: str, port: int = 22, username: str = 'user', password: str = 'password'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
       
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, username=self.username, password=self.password, port=self.port)
            print(f"Connected to {self.host}")
        except Exception as e:
            print(f"Connection failed: {e}")
            raise

    def execute_command(self, command: str) -> str:
      
        if not self.client:
            self.connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode()
        error = stderr.read().decode()
        return output if output else error

    def close(self):
        
        if self.client:
            self.client.close()
            print(f"Connection closed to {self.host}")

    async def execute_concurrently(self, commands: List[str]) -> List[str]:
        
        results = await asyncio.gather(*[self.run_command_async(command) for command in commands])
        return results

    async def run_command_async(self, command: str) -> str:
       
        return await asyncio.to_thread(self.execute_command, command)

@app.post("/run_commands/")
async def run_commands(commands: List[str], background_tasks: BackgroundTasks):
    
    client = SSHClientManager("192.168.1.1")  
    background_tasks.add_task(client.connect)
    result = await client.execute_concurrently(commands)
    client.close()
    return {"results": result}
