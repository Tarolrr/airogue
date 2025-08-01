"""
Isolated test that demonstrates the OpenAI API key requirement.

This test intentionally does not use any mocks to demonstrate the external 
dependency on OpenAI API keys. This file should be used as a reference for
future refactoring to properly decouple the application from external dependencies.
"""
import pytest
import os
from unittest.mock import patch


class TestOpenAIKeyRequirement:
    """Tests that isolate the OpenAI API key requirement."""
    
    def test_world_instantiation_requires_api_key(self):
        """
        Demonstrate that instantiating World requires an OpenAI API key.
        
        This test confirms that while module imports are now decoupled from API key requirements,
        actually instantiating and using the World class still requires an API key.
        """
        # Ensure no OPENAI_API_KEY is set
        with patch.dict(os.environ, {}, clear=True):
            import llm.world
            # Now imports work, but instantiation should fail
            with pytest.raises(Exception) as excinfo:
                world = llm.world.World("test setting")
            
            # Verify the error is related to OpenAI API key
            assert "api_key" in str(excinfo.value).lower()
            assert "openai" in str(excinfo.value).lower()
