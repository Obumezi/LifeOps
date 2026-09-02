from strands import Agent
from strands.models import BedrockModel


model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-east-1",
    temperature=0.2,
)


agent = Agent(
    model=model,
    system_prompt="""
You are the LifeOps connectivity test agent.

Respond briefly and confirm that you are running
through Strands Agents using Amazon Bedrock.
"""
)


response = agent(
    "Confirm that the LifeOps Bedrock connection is working."
)


print("\n=== LIFEOPS STRANDS TEST ===\n")
print(response)
print("\n============================\n")