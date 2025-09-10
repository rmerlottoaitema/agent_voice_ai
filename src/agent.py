import json
import logging
import os
from livekit import api
from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
)
from livekit.agents.llm import function_tool
from livekit.agents.voice import MetricsCollectedEvent
from livekit.plugins import cartesia, deepgram, noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

logger = logging.getLogger("agent")

load_dotenv(".env.local")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            Your responses are concise, to the point, and without any complex formatting or punctuation.
            You are curious, friendly, and have a sense of humor.""",
        )

    @function_tool
    async def lookup_weather(self, context: RunContext, location: str):
        """Use this tool to look up current weather information in the given location.

        If the location is not supported by the weather service, the tool will indicate this. You must tell the user the location's weather is unavailable.

        Args:
            location: The location to look up weather information for (e.g. city name)
        """

        logger.info(f"Looking up weather for {location}")
        return "sunny with a temperature of 70 degrees."


async def entrypoint(ctx: JobContext):
    # Load VAD directly in the entrypoint
    vad = silero.VAD.load()
    
    # Initialize phone_number as None
    phone_number = None
    sip_participant_identity = None
    
    # Only try to parse metadata if it exists and is not empty
    if ctx.job.metadata and ctx.job.metadata.strip():
        try:
            dial_info = json.loads(ctx.job.metadata)
            phone_number = dial_info.get("phone_number")
            sip_participant_identity = phone_number
        except json.JSONDecodeError:
            logger.warning("Invalid JSON metadata, ignoring")
    
    # Only attempt SIP call if phone_number is provided and valid
    if phone_number:
        try:
            await ctx.api.sip.create_sip_participant(api.CreateSIPParticipantRequest(
                room_name=ctx.room.name,
                sip_trunk_id='ST_ogziJLEJJqcc',
                sip_call_to=phone_number,
                participant_identity=sip_participant_identity,
                wait_until_answered=True,
            ))
            print("call picked up successfully")
        except api.TwirpError as e:
            print(f"error creating SIP participant: {e.message}, "
                  f"SIP status: {e.metadata.get('sip_status_code')} "
                  f"{e.metadata.get('sip_status')}")
            ctx.shutdown()
            return
    
    # Add context to log entries
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up voice AI pipeline
    session = AgentSession(
        llm=openai.LLM(model="gpt-4o-mini"),
        stt=deepgram.STT(model="nova-3", language="multi"),
        tts=cartesia.TTS(voice="6f84f4b8-58a2-430c-8c79-688dad597532"),
        turn_detection=MultilingualModel(),
        vad=vad,
    )

    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    # Only greet if this is an inbound call (no phone number provided)
    if phone_number is None:
        await session.generate_reply(
            instructions="Greet the user and offer your assistance."
        )

    # Join the room and connect to the user
    await ctx.connect()

if __name__ == "__main__":
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint,
        agent_name="my-telephony-agent"
    ))