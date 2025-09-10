import asyncio
import os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession
from livekit.agents.job import JobContext
from livekit.plugins import openai, deepgram, cartesia, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.api.access_token import AccessToken, VideoGrants
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sip-room-agent")

load_dotenv(".env.local")

class SimpleAssistant(Agent):
    def __init__(self):
        super().__init__(
            instructions="You are a helpful voice assistant. Be concise and friendly."
        )

async def connect_to_sip_room():
    """Connetti direttamente a sip-room usando lo stesso metodo del server"""
    logger.info("🔗 Connecting directly to sip-room...")
    
    LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
    LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
    
    try:
        at = AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        at.with_identity("sip-room-agent")
        
        # Create VideoGrants
        grants = VideoGrants()
        grants.room = "sip-room"
        grants.room_join = True
        grants.can_publish = True
        grants.can_subscribe = True
        
        at.with_grants(grants)
        at.with_ttl(datetime.timedelta(hours=1))
        token = at.to_jwt()
        
        logger.info("Token generated for sip-room")
        return token
        
    except Exception as e:
        logger.error(f"Token generation failed: {e}")
        return None

async def entrypoint(ctx: JobContext):
    """Entrypoint ignore fake_human """
    
    logger.info(f"🔍 Agent in room: {ctx.room.name}")
    
    # Filter only real partecipant (no fake_human)
    real_participants = [p for p in ctx.room.remote_participants.values() if p.identity != "fake_human"]
    logger.info(f"👥 Real participants: {[p.identity for p in real_participants]}")
    
    if "fake_human" in [p.identity for p in ctx.room.remote_participants.values()]:
        logger.info("⏳ Waiting for REAL participants (ignoring fake_human)...")
        
        try:
            session = AgentSession(
                llm=openai.LLM(model="gpt-4o-mini"),
                stt=deepgram.STT(model="nova-3", language="multi"),
                tts=cartesia.TTS(voice="6f84f4b8-58a2-430c-8c79-688dad597532"),
                turn_detection=MultilingualModel(),
            )
            
            await session.start(
                agent=SimpleAssistant(),
                room=ctx.room,
                room_input_options=noise_cancellation.BVC(),
            )
            
            logger.info("Agent ready for REAL participants!")
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return
    
    # Listen only real partecipant
    @ctx.room.on("participant_connected")
    def on_participant_connected(participant):
        if participant.identity == "fake_human":
            logger.debug("Ignoring fake_human")
            return
            
        logger.info(f"REAL PARTICIPANT CONNECTED: {participant.identity}")
        
        asyncio.create_task(session.generate_reply(
            instructions="Greet the user warmly and offer your assistance."
        ))
    
    logger.info("Waiting for REAL participants...")
    
    try:
        while True:
            await asyncio.sleep(5)
            real_participants = [p for p in ctx.room.remote_participants.values() if p.identity != "fake_human"]
            
            if real_participants:
                logger.info(f"Real participants: {[p.identity for p in real_participants]}")
            else:
                logger.debug("Still waiting for real participants...")
                
    except asyncio.CancelledError:
        logger.info("Agent shutting down...")

if __name__ == "__main__":
    from livekit.agents import cli, WorkerOptions
    
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="sip-room-telephony-agent"
        )
    )