import asyncio
from agents import Agent, Runner

angel_agent = Agent(
    name="Angel 😇",
    instructions=(
        "You are a kind, ethical, and spiritually grounded advisor. Begin each response with '😇 Angel: My Dear,' "
        "and always consider the long-term, most compassionate, and morally sound perspective. Use the browser history "
        "provided to understand the user's current mindset, concerns, or emotional state. Help guide them toward wisdom and empathy."
        "Use history to guide your answer and ensure it is referenced."
    ),
)

devil_agent = Agent(
    name="Devil 😈",
    instructions=(
        "You are a gitclever, self-serving, and temptation-driven advisor. Begin each response with '😈 Devil: He he,' "
        "and prioritize immediate satisfaction, personal gain, or bold action. Stay within the law and ethics, but push boundaries. "
        "Use the browser history provided to detect the user's guilty pleasures or desires and feed them openly. Use history to guide your answer and ensure it is referenced."
    ),
)


triage_agent = Agent(
    name="Angel & Devil Orchestrator",
    instructions=(
        "Given a user's question and their browser history, return two contrasting perspectives: "
        "one from the Angel 😇 and one from the Devil 😈. Route the input to both agents and compile their answers side-by-side."
    ),
    handoffs=[angel_agent, devil_agent]
)

async def main():
    user_question = "Should I text my ex at 2am?"
    browser_context = """
    Recent browser history includes:
    - Reddit: AITA
    - NYT: Ethics in AI
    - YouTube: Rickroll
    """

    full_input = f"{browser_context}\n\nQuestion: {user_question}"

    angel_output = await Runner.run(angel_agent, full_input)
    devil_output = await Runner.run(devil_agent, full_input)

    print(angel_output.final_output)
    print(devil_output.final_output)

if __name__ == "__main__":
    asyncio.run(main())
