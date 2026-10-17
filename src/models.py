"""Build an OpenAI client for any OpenAI-compatible endpoint listed in config.yaml."""
from openai import OpenAI


def build_client(model_cfg: dict) -> OpenAI:
    return OpenAI(base_url=model_cfg["base_url"], api_key=model_cfg["api_key"])
