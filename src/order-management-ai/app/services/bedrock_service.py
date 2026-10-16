import boto3
from botocore.exceptions import ClientError

from app.core.config import settings
from app.services.llm_service import LLMService


class BedrockService(LLMService):
    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.aws_region,
        )

    def chat(self, message: str) -> str:
        try:
            response = self.client.converse(
                modelId=settings.bedrock_model_id,
                system=[
                    {
                        "text": (
                            "You are the OMS AI Assistant. "
                            "Be concise, accurate, and helpful."
                        )
                    }
                ],
                messages=[
                    {
                        "role": "user",
                        "content": [{"text": message}],
                    }
                ],
                inferenceConfig={
                    "maxTokens": 100,
                    "temperature": 0.3,
                    "topP": 0.9,
                },
            )

            content = response["output"]["message"]["content"]

            text_block = next(
                (
                    block["text"]
                    for block in content
                    if "text" in block
                ),
                None,
            )

            if not text_block:
                raise RuntimeError(
                    "Bedrock returned no text response."
                )

            return text_block

        except ClientError as exc:
            raise RuntimeError(
                f"Bedrock request failed: {exc}"
            ) from exc