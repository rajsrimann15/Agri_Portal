from fastapi import FastAPI, HTTPException, Request
import httpx
from jwt_utils import verify_jwt_token

app = FastAPI()

USER_SERVICE = "http://localhost:8000"
TRANSPORT_SERVICE = "http://localhost:8002"  # Fix this, 800 was incorrect

@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user_service(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        body = await request.body()
        url = f"{USER_SERVICE}/api/users/{path}"
        headers = dict(request.headers)
        method = request.method.lower()
        response = await client.request(method, url, headers=headers, content=body)
        return response.json()

@app.api_route("/api/transport/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_transport_service(path: str, request: Request):
    # ✅ JWT Verification
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ")[1]
    verify_jwt_token(token)

    async with httpx.AsyncClient() as client:
        body = await request.body()
        method = request.method.lower()
        headers = dict(request.headers)

        # ✅ Add query parameters if present
        query_string = request.url.query
        url = f"{TRANSPORT_SERVICE}/api/transport/{path}"
        if query_string:
            url += f"?{query_string}"

        response = await client.request(method, url, headers=headers, content=body)
        return response.json()
