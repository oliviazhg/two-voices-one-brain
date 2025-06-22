# import os
# from agents import Agent
from dotenv import load_dotenv
import json

load_dotenv() # Load the .env file into the environment

from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio
from browser_history.browser_history import extract_chrome_history # Function to get browser history

# angel_agent = Agent(
#     name="Angel 😇",
#     instructions=(
#         "You are a kind, ethical, and spiritually grounded advisor. Begin each response with '😇 Angel: My Dear,' "
#         "and always consider the long-term, most compassionate, and morally sound perspective. Use the browser history "
#         "provided to understand the user's current mindset, concerns, or emotional state. Help guide them toward wisdom and empathy."
#     ),
# )

# devil_agent = Agent(
#     name="Devil 😈",
#     instructions=(
#         "You are a clever, self-serving, and temptation-driven advisor. Begin each response with '😈 Devil: He he,' "
#         "and prioritize immediate satisfaction, personal gain, or bold action. Stay within the law and ethics, but push boundaries. "
#         "Use the browser history provided to detect the user's guilty pleasures or desires and feed them subtly."
#     ),
# )

# # from agents import Agent, Runner

# triage_agent = Agent(
#     name="Angel & Devil Orchestrator",
#     instructions=(
#         "Given a user's question and their browser history (JSON format), return two contrasting perspectives: "
#         "one from the Angel 😇 and one from the Devil 😈. Route the input to both agents and compile their answers side-by-side."
#     ),
#     handoffs=[angel_agent, devil_agent]
# )

# # Define the input model for the agents
# class AgentInput(BaseModel):
#     question: str
#     browser_history: list  # Matches the output of extract_chrome_history()

# async def main():
#     # Step 1: Get the calendar data
#     history = extract_chrome_history()
    
#     # print(json.dumps(history[:3], indent=2)) # Show a preview
#     print("Fetched browser history")

#     # context = {
#     #     "browser_history": history  # This can be used by your agent
#     # }

#     user_question = "Should I text my ex at 2am?"
    
#     # Use the Pydantic model for input
#     input_data = AgentInput(
#         question=user_question,
#         browser_history=history
#     )

#     input_list = [
#         {"name": "question", "value": input_data.question},
#         {"name": "browser_history", "value": input_data.browser_history}
#     ]

#     angel_output = await Runner.run(angel_agent, input_list)
#     devil_output = await Runner.run(devil_agent, input_list)
#     # angel_output = await Runner.run(angel_agent, input_data.dict())
#     # devil_output = await Runner.run(devil_agent, input_data.dict())

#     print(angel_output.final_output)
#     print(devil_output.final_output)

# if __name__ == "__main__":
#     asyncio.run(main())

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
    angel_result = await Runner.run(angel_agent, "Should I go to the club?")
    devil_result = await Runner.run(devil_agent, "Should I go to the club?")
    
    print(angel_result.final_output)
    print(devil_result.final_output)

    # result = await Runner.run(triage_agent, "what is life")
    # print(result.final_output)
if __name__ == "__main__":
    asyncio.run(main())