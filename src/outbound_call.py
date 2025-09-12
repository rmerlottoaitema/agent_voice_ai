import asyncio
from dotenv import load_dotenv
from livekit import api 
from livekit.protocol.sip import CreateSIPParticipantRequest, SIPParticipantInfo


load_dotenv(".env.local")


async def main():
    livekit_api = api.LiveKitAPI()

    request = CreateSIPParticipantRequest(
        sip_trunk_id = "ST_j3Hr2hiQgHHs",
        sip_call_to = "+12082790589",
        room_name = "sip-room",
        participant_identity = "sip-test",
        participant_name = "Test Caller"
    )
    
    try:
        participant = await livekit_api.sip.create_sip_participant(request)
        print(f"Successfully created {participant}")
    except Exception as e:
        print(f"Error creating SIP participant: {e}")
    finally:
        await livekit_api.aclose()

asyncio.run(main())