from fastapi import FastAPI, Request, Header, HTTPException
from dotenv import load_dotenv
import uvicorn
import base64
import hashlib
import hmac
import os

def valid_signature(signing_token, message_id, timestamp, body, received_signatures):
    raw_key = base64.b64decode(signing_token.removeprefix('whsec_'))
    message = f"{message_id}.{timestamp}.{body}".encode('utf-8')
    digest = hmac.new(raw_key, message, hashlib.sha256).digest()
    expected = "v1," + base64.b64encode(digest).decode('utf-8')
    return any(
        hmac.compare_digest(expected, sig)
        for sig in received_signatures.split(' ')
    )

load_dotenv()

app = FastAPI(docs_url=None,redoc_url=None)
signing_token = os.environ.get("SIGNING_TOKEN")

@app.post("/")
async def handle_webhook(
                   req: Request,
                   webhook_id: str = Header(None),
                   webhook_timestamp: str = Header(None),
                   webhook_signature: str = Header(None)
                  ):
    body = await req.body()
    if valid_signature(signing_token, webhook_id, webhook_timestamp, body.decode('utf-8'), webhook_signature):
        print("Pulling new zone files")
        os.system("git reset --hard && git pull")
        rc = os.system("systemctl reload nsd")
        if rc == 0:
            print("Success")
            return
        else:
            print("Error when reloading NSD")
            raise HTTPException(status_code=500, detail="Error when reloading NSD")
    else:
        print("Bad signature!")
        raise HTTPException(status_code=401, detail="Bad signature")


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8080)