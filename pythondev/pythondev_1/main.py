import asyncio
import asyncssh
from fastapi import FastAPI, HTTPException
from typing import List
import ipaddress

app = FastAPI()


SSH_USER = "user_name"
SSH_PASSWORD = "password"


network = ipaddress.ip_network("172.29.0.0/16")

async def scan_ip(ip: str) -> bool:
    
    try:
        async with asyncssh.connect(ip, username=SSH_USER, password=SSH_PASSWORD, known_hosts=None) as conn:
            return True
    except (asyncssh.Error, OSError):
        return False

async def scan_network() -> List[str]:
    
    tasks = []
    reachable_ips = []

   
    for ip in network.hosts():
        tasks.append(scan_ip(str(ip)))


    results = await asyncio.gather(*tasks)

 
    for ip, success in zip(network.hosts(), results):
        if success:
            reachable_ips.append(str(ip))

    return reachable_ips

@app.get("/scan")
async def scan_network_endpoint():
    
    reachable_ips = await scan_network()  
    if not reachable_ips:
        raise HTTPException(status_code=404, detail="No reachable IPs found")
    return {"reachable_ips": reachable_ips}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
