from fastapi import FastAPI, Request, Header, status
from dotenv import load_dotenv
from annotated_types import Annotated
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
signing_token = os.environ.get("SIGNING_TOKEN") or ""

@app.post("/")
def handle_webhook(
                   req: Request, 
                   webhook_id: Annotated[str | None, Header()] = None,
                   webhook_timestamp: Annotated[str | None, Header()] = None,
                   webhook_signature: Annotated[str | None, Header()] = None
                  ):
    if valid_signature(signing_token, webhook_id, webhook_timestamp, req.body(), webhook_signature):
        print("Pulling new zone files")
        os.system("git reset --hard && git pull")
        rc = os.system("systemctl reload nsd")
        if rc == 0:
            print("Success")
            return status.HTTP_200_OK
        else:
            print("Error when reloading NSD")
            return status.HTTP_500_INTERNAL_SERVER_ERROR
    else:
        print("Bad signature!")
        return status.HTTP_401_UNAUTHORIZED


if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8080)