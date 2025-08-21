from connection import config
from pydantic import BaseModel
from agents import (Agent, Runner, input_guardrail,
                    GuardrailFunctionOutput, InputGuardrailTripwireTriggered)
import asyncio
import rich
from dotenv import load_dotenv

load_dotenv()


class FatherGuardrailOutput(BaseModel):
    response: str
    is_too_cold: bool


father_guardrail_agent = Agent(
    name="Father Guardrail Agent",
    instructions=""" 
        You're acting as a protective father.
        If the child tries to run when temperature is below 26°C, stop them gently.
    """,
    output_type=FatherGuardrailOutput
)


@input_guardrail
async def check_temperature_guardrail(ctx, agent, input):
    result = await Runner.run(father_guardrail_agent, input, run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_too_cold
    )

father_agent = Agent(
    name='Father Agent',
    instructions=""" You are a caring father. You can respond to your child's requests,
        but are restricted by guardrails to prevent unsafe actions..""",
    input_guardrails=[check_temperature_guardrail]
)


async def main():
    try:
        user_input = str(input("Child's request: "))
        result = await Runner.run(father_agent, user_input, run_config=config)
        print("Request approved.")

    except InputGuardrailTripwireTriggered:
        print("No, it's too cold to go out! Stay inside.")


if __name__ == "__main__":
    asyncio.run(main())