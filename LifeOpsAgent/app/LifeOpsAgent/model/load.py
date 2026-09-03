from strands.models.bedrock import BedrockModel


def load_model() -> BedrockModel:
    """Load the Bedrock model used by LifeOps."""
    return BedrockModel(
        model_id="global.anthropic.claude-sonnet-4-6",
        region_name="us-east-1",
        temperature=0.2,
    )