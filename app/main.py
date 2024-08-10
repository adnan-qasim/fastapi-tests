import json
from typing import Optional
from fastapi import FastAPI
import consul , socket

app = FastAPI()


@app.get("/hello")
def read_root():
    return {"message":"hello world"}

def get_ip_address():
    # Fetching IP address by creating a UDP connection to a public server (Google DNS)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = requests.get('https://api.ipify.org').text  
        s.close()
    return ip_address


@app.on_event("startup")
async def register_with_consul():
    client = consul.Consul(host='localhost', port=8500)
    service_id = "my-fastapi-service"
    ip_address = get_ip_address()
    client.agent.service.register(
        name="fastapi-service",
        service_id=service_id,
        address=ip_address,
        port=8000,
        tags=["fastapi", "python"],
        check=consul.Check.http("http://127.0.0.1:8000/health", interval="10s")
    )
@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("shutdown")
async def deregister_from_consul():
    client = consul.Consul(host='localhost', port=8500)
    service_id = "my-fastapi-service"
    client.agent.service.deregister(service_id)

@app.get("/")
async def read_root():
    return {"Hello": "World"}
