"""
watsonx_client.py
IBM watsonx.ai Client Wrapper.
Handles authentication and LLM inference calls via the IBM watsonx.ai
Foundation Models API (ibm-watson-machine-learning / ibm-watsonx-ai SDK).
"""
import os
from typing import Optional

# IBM watsonx.ai SDK (ibm-watsonx-ai)
try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    WATSONX_AVAILABLE = True
except ImportError:
    WATSONX_AVAILABLE = False


# ── Configuration (loaded from environment variables / .env) ──────────────────
WATSONX_API_KEY    = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL        = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")
WATSONX_MODEL_ID   = os.getenv("WATSONX_MODEL_ID", "ibm/granite-13b-chat-v2")

# Generation parameters
_GEN_PARAMS = {
    "max_new_tokens": 800,
    "temperature":    0.7,
    "top_p":          0.9,
    "repetition_penalty": 1.1,
}


class WatsonxClient:
    """
    Thin wrapper around IBM watsonx.ai ModelInference for text generation.
    Falls back to a stub response if credentials are not configured.
    """

    def __init__(self):
        self._model: Optional[object] = None
        self._initialized = False
        self._init_error: str = ""
        self._try_init()

    def _try_init(self):
        if not WATSONX_AVAILABLE:
            self._init_error = (
                "ibm-watsonx-ai package not installed. "
                "Run: pip install ibm-watsonx-ai"
            )
            return
        if not WATSONX_API_KEY or not WATSONX_PROJECT_ID:
            self._init_error = (
                "WATSONX_API_KEY or WATSONX_PROJECT_ID not set. "
                "Configure your .env file."
            )
            return
        try:
            credentials = Credentials(
                url=WATSONX_URL,
                api_key=WATSONX_API_KEY,
            )
            self._model = ModelInference(
                model_id=WATSONX_MODEL_ID,
                credentials=credentials,
                project_id=WATSONX_PROJECT_ID,
                params=_GEN_PARAMS,
            )
            self._initialized = True
        except Exception as exc:
            self._init_error = str(exc)

    @property
    def is_ready(self) -> bool:
        return self._initialized

    def generate(self, prompt: str) -> str:
        """
        Send a prompt to IBM watsonx.ai and return the generated text.
        Falls back to a local stub response when credentials are unavailable.
        """
        if not self._initialized:
            return self._stub_response(prompt)

        try:
            response = self._model.generate_text(prompt=prompt)
            return response.strip()
        except Exception as exc:
            return f"[watsonx.ai error: {exc}]"

    def _stub_response(self, prompt: str) -> str:
        """
        Local stub used when watsonx credentials are not configured.
        Provides a helpful placeholder so the UI still works for demo/testing.
        """
        return (
            "⚠️  IBM watsonx.ai is not connected. "
            f"({self._init_error})\n\n"
            "To enable AI-powered responses:\n"
            "1. Copy .env.example → .env\n"
            "2. Fill in WATSONX_API_KEY and WATSONX_PROJECT_ID\n"
            "3. Restart the agent\n\n"
            "The rule-based analysis and tips modules are fully functional "
            "and will continue to provide energy insights."
        )


# Singleton instance
_client: Optional[WatsonxClient] = None


def get_watsonx_client() -> WatsonxClient:
    global _client
    if _client is None:
        _client = WatsonxClient()
    return _client
