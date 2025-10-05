# agent_main.py
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import noise_cancellation
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from booking_tools import check_availability_tool, create_booking_tool
load_dotenv()
from livekit.plugins import google

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.8,
            ),
                tools=[
                    check_availability_tool,
                    create_booking_tool
                ],
        )

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    # Kick off the session with instructions for the reservation task
    await session.generate_reply(
        instructions=SESSION_INSTRUCTION,
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
