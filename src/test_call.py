import os
import asyncio
import aiohttp
import json
from livekit import api

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
LIVEKIT_URL = "https://aitematest-fmet0mg5.livekit.cloud"

async def make_sip_call():
    url = f"{LIVEKIT_URL}/twirp/livekit.SIP/SIPDispatchCall"

    # Genera JWT Bearer token
    token = api.AccessToken(api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET)
    jwt = token.with_identity("sip-caller").to_jwt()


    payload = {
            "sip_trunk_id": "ST_jRRjxELq4ttH",
            "to": "+15105550100",          
            "room_name": "sip-test-room",
            "participant_identity": "sip-caller",
    }

    headers = {
       "Authorization": f"Bearer {jwt}",
       "Content-Type": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(payload)) as resp:
            print("Status:", resp.status)
            text = await resp.text()
            print("Response:", text)

if __name__ == "__main__":
    asyncio.run(make_sip_call())
