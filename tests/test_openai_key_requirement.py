"""Tests for lazy construction of the compatibility ``World`` wrapper."""
import os
from unittest.mock import patch


class TestOpenAIKeyRequirement:
    """Construction must not require credentials before a generation call."""
    
    def test_world_instantiation_does_not_require_api_key(self):
        """The provider is chosen lazily so Codex needs no OpenAI key at setup."""
        with patch.dict(os.environ, {}, clear=True):
            import llm.world

            world = llm.world.World("test setting")

        assert world.setting == "test setting"
