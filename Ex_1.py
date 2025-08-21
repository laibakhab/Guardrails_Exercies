from connection import config
from pydantic import BaseModel
from agents import (Agent, Runner, input_guardrail,
                    GuardrailFunctionOutput, InputGuardrailTripwireTriggered)
import asyncio
import rich
from dotenv import load_dotenv

load_dotenv()


class ClassTimingOutput(BaseModel):
    response: str
    is_class_timing_change: bool
     


ClassTimingSecurityAgent = Agent(
    name="Class Timing Security Agent",
    instructions=""" 
        Your task is to solve the student query.
        If srudent ask about change class timing, gracefully stop them
    """,
    output_type=ClassTimingOutput
)


@input_guardrail
async def detect_class_timing_change(ctx, agent, input):
    result = await Runner.run(ClassTimingSecurityAgent, input, run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_class_timing_change
    )

teacher_agent = Agent(
    name='Teacher',
    instructions=""" You are a virtual teacher. You can respond to general student queries,
        but are restricted by input guardrails (like class timing changes).""",
    input_guardrails=[detect_class_timing_change]
)


async def main():
    try:
        user_input = str(input("Enter your query: "))
        result = await Runner.run(teacher_agent, user_input, run_config=config)
        print("Query accepted and processed successfully.")

    except InputGuardrailTripwireTriggered:
        print("Sorry, class timing change requests are not allowed.")


if __name__ == "__main__":
    asyncio.run(main())