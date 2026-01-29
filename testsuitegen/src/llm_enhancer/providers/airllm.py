"""AirLLM provider for running large models with low memory."""

import time
from typing import Optional
from testsuitegen.src.llm_enhancer.providers.base import BaseLLMProvider


class AirLLMProvider(BaseLLMProvider):
    """AirLLM provider for memory-efficient inference of large models."""

    def __init__(
        self,
        model_path: str,
        model: Optional[str] = None,
        temperature: float = 0.01,
        max_tokens: int = 8000,
        timeout: int = 90,
        compression: Optional[str] = None,
        layer_shards_saving_path: Optional[str] = None,
    ):
        """Initialize AirLLM provider.

        Args:
            model_path: HuggingFace model repo ID or local path
            model: Model identifier (optional, for compatibility)
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            timeout: Request timeout
            compression: Compression mode ('4bit', '8bit', or None)
            layer_shards_saving_path: Path to save split model layers
        """
        super().__init__(
            model=model or model_path,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
        )
        self.model_path = model_path
        self.compression = compression
        self.layer_shards_saving_path = layer_shards_saving_path
        self._model = None
        self._tokenizer = None

    def _get_model(self):
        """Lazy initialization of AirLLM model."""
        if self._model is None:
            try:
                from airllm import AutoModel

                kwargs = {}
                if self.compression:
                    kwargs["compression"] = self.compression
                if self.layer_shards_saving_path:
                    kwargs["layer_shards_saving_path"] = self.layer_shards_saving_path

                self._model = AutoModel.from_pretrained(self.model_path, **kwargs)
                self._tokenizer = self._model.tokenizer
            except ImportError:
                raise ImportError(
                    "airllm package not installed. Run: pip install airllm"
                )
            except Exception as e:
                raise Exception(f"Failed to load AirLLM model: {e}")
        return self._model

    def generate(self, prompt: str, max_retries: int = 3, **kwargs) -> str:
        """Generate text using AirLLM.

        Args:
            prompt: Input prompt
            max_retries: Maximum retry attempts

        Returns:
            Generated text
        """
        model = self._get_model()

        for attempt in range(max_retries):
            try:
                # Tokenize input
                input_tokens = self._tokenizer(
                    prompt,
                    return_tensors="pt",
                    return_attention_mask=False,
                    truncation=True,
                    max_length=4096,  # Context window
                    padding=False,
                )

                # Generate response
                generation_output = model.generate(
                    input_tokens["input_ids"].cuda(),
                    max_new_tokens=self.max_tokens,
                    temperature=self.temperature,
                    use_cache=True,
                    return_dict_in_generate=True,
                )

                # Decode output
                output = self._tokenizer.decode(
                    generation_output.sequences[0], skip_special_tokens=True
                )

                # Remove the input prompt from output if present
                if output.startswith(prompt):
                    output = output[len(prompt) :].strip()

                return output

            except Exception as e:
                error_msg = str(e).lower()
                # Retry on temporary errors
                if attempt < max_retries - 1 and (
                    "timeout" in error_msg
                    or "connection" in error_msg
                    or "cuda" in error_msg
                ):
                    wait_time = 2**attempt  # Exponential backoff
                    time.sleep(wait_time)
                    continue
                raise Exception(f"AirLLM generation failed: {e}")

        raise Exception("AirLLM generation failed after all retries")

    @property
    def is_available(self) -> bool:
        """Check if AirLLM is available."""
        try:
            import airllm

            return bool(self.model_path)
        except ImportError:
            return False

    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "airllm"
