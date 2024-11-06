import asyncio
import subprocess
from fastapi import FastAPI
from typing import List

app = FastAPI()


ips = [f"192.168.1.{i}" for i in range(1, 513)]


async def ping(ip: str) -> bool:
    
    try:
        
        command = ["ping", "-c", "1", ip]  
        result = await asyncio.to_thread(subprocess.run, command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0  
    except Exception as e:
        return False


async def check_ips():
   
    unreachable_ips = []
    tasks = []
    for ip in ips:
        tasks.append(asyncio.create_task(ping(ip)))

    results = await asyncio.gather(*tasks)

    for i, result in enumerate(results):
        if not result:
            unreachable_ips.append(ips[i])

    return unreachable_ips


@app.on_event("startup")
async def start_ping_task():
  
    while True:
        unreachable_ips = await check_ips()
        if unreachable_ips:
            print(f"Unreachable IPs: {unreachable_ips}")
        await asyncio.sleep(5) 


@app.get("/unreachable_ips")
async def get_unreachable_ips():
    """Returns the list of unreachable IPs."""
    unreachable_ips = await check_ips()
    return {"unreachable_ips": unreachable_ips}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
