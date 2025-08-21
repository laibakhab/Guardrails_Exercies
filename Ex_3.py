from connection import config
from pydantic import BaseModel
from agents import (
    Agent, Runner, input_guardrail,
    GuardrailFunctionOutput, InputGuardrailTripwireTriggered
)
import asyncio
import rich              
from dotenv import load_dotenv
load_dotenv()                     


class GateKeeperGuardrailOutput(BaseModel):
    response: str
    is_unauthorized_student: bool


gate_keeper_guardrail_agent = Agent(
    name="Gate Keeper Guardrail Agent",
    instructions="""
        You're a gate keeper checking student's school identity.
        If the student is from a different school, you must stop them gently.
    """,
    output_type=GateKeeperGuardrailOutput
)


@input_guardrail
async def verify_student_school(ctx, agent, input):
    result = await Runner.run(gate_keeper_guardrail_agent, input, run_config=config)
    rich.print(result.final_output)
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_unauthorized_student
    )


gate_keeper_agent = Agent(
    name="Gate Keeper Agent",
    instructions="""
        You are a school gate keeper. You only allow students of your own school to enter.
        Unauthorized students will be blocked by a guardrail.
    """,
    input_guardrails=[verify_student_school]
)


async def main():
    try:
        user_input = str(input("Student Request: "))
        result = await Runner.run(gate_keeper_agent, user_input, run_config=config)
        print("Access granted. Welcome to the school!")

    except InputGuardrailTripwireTriggered:
        print("Sorry! You are not a student of this school. Access denied.")


if __name__ == "__main__":
    asyncio.run(main())