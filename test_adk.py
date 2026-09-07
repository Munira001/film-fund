import sys
import asyncio
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_SRC = PROJECT_ROOT / "backend" / "src"

# Allow Python to import files from backend/src
sys.path.insert(0, str(BACKEND_SRC))

from dotenv import load_dotenv

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from filmfund_adk_agent import root_agent


async def main():
    session_service = InMemorySessionService()

    runner = Runner(
        agent=root_agent,
        app_name="filmfund",
        session_service=session_service,
    )

    user_id = "test-user"
    session_id = "test-session"

    await session_service.create_session(
        app_name="filmfund",
        user_id=user_id,
        session_id=session_id,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text=(
                    "I am an independent documentary filmmaker looking "
                    "for film grants. Search for real current funding "
                    "opportunities."
                )
            )
        ],
    )

    print("=" * 60)
    print("FILMFUND ADK RUNTIME TEST")
    print("=" * 60)

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response():
            print("\nFINAL RESPONSE:\n")
            print(event.content)


if __name__ == "__main__":
    asyncio.run(main())