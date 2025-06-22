# import os
# from agents import Agent
from dotenv import load_dotenv
import json

load_dotenv() # Load the .env file into the environment

from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio
from browser_history.browser_history import extract_chrome_history # Function to get browser history

class DecisionOutput(BaseModel):
    is_safe: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about lighthearted decisions.",
    output_type=DecisionOutput,
)

angel_agent = Agent(
    name="Angel 😇",
    instructions=(
        "You are a kind, ethical, and spiritually grounded advisor. Begin each response with '😇 Angel: My Dear,' "
        "and always consider the long-term, most compassionate, and morally sound perspective. Use the browser history "
        "provided to understand the user's current mindset, concerns, or emotional state. Help guide them toward wisdom and empathy."
    ),
)

devil_agent = Agent(
    name="Devil 😈",
    instructions=(
        "You are a clever, self-serving, and temptation-driven advisor. Begin each response with '😈 Devil: He he,' "
        "and prioritize immediate satisfaction, personal gain, or bold action. Stay within the law and ethics, but push boundaries. "
        "Use the browser history provided to detect the user's guilty pleasures or desires and feed them subtly."
    ),
)


async def decision_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(DecisionOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_safe,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's  question",
    handoffs=[angel_agent, devil_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=decision_guardrail),
    ],
)

async def main():
    # Get user data
    history = extract_chrome_history() # Get browser history

    angel_result = await Runner.run(angel_agent, "Should I go to the club?")
    devil_result = await Runner.run(devil_agent, "Should I go to the club?")
    
    print(angel_result.final_output)
    print(devil_result.final_output)

if __name__ == "__main__":
    asyncio.run(main())