"""
LLM Factory module for creating LangChain LLM instances based on configuration.
Supports Groq (Cloud) and Ollama (Local) providers.
"""

from __future__ import annotations
from typing import Optional, Union

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from src.config.settings import Settings
from src.utils.logger import setup_logger

logger = setup_logger("llm_factory")

class LLMFactory:
    """
    Factory class to instantiate LLM providers consistently across agents.
    """

    @staticmethod
    def create_llm(
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.0
    ) -> Optional[Union[ChatGroq, ChatOllama]]:
        """
        Create and return an LLM instance based on the provider.
        
        Args:
            provider: 'groq' or 'ollama'. Defaults to Settings.LLM_PROVIDER.
            model: Model name string. Defaults to Settings.LLM_MODEL.
            temperature: Sampling temperature.
            
        Returns:
            An initialized LLM instance or None if in Demo Mode.
        """
        provider = (provider or Settings.LLM_PROVIDER).lower()
        model = model or Settings.LLM_MODEL
        
        # 1. Ollama (Local)
        if provider == "ollama":
            try:
                llm = ChatOllama(
                    model=model,
                    temperature=temperature,
                    base_url=Settings.OLLAMA_BASE_URL
                )
                logger.info(f"Initialized Local LLM (Ollama: {model})")
                return llm
            except Exception as e:
                logger.error(f"Failed to initialize Ollama: {e}")
                return None

        # 2. Groq (Cloud)
        if provider == "groq" and Settings.GROQ_API_KEY:
            try:
                llm = ChatGroq(
                    model_name=model,
                    temperature=temperature,
                    api_key=Settings.GROQ_API_KEY
                )
                logger.info(f"Initialized Cloud LLM (Groq: {model})")
                return llm
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
                return None

        # 3. Fallback / Demo Mode
        logger.info(f"LLM Factory: Demo Mode or Invalid Config (Provider={provider})")
        return None
