import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type
)

# Robust retry configuration
# wait_exponential_jitter: exp backoff (2^n) + random jitter to avoid thundering herd
# stops after 6 attempts (approx 60-100s total wait time)
# catches RateLimitError specifically

def is_transient_error(exception):
    """Checks for rate limits or overloaded servers across providers."""
    msg = str(exception).lower()
    return any(term in msg for term in ["rate limit", "too many requests", "quota exceeded", "overloaded", "server error"])

RETRY_DECORATOR = retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=2, max=30),
    retry=lambda e: is_transient_error(e)
)

# A more specific version that only retries on likely transient errors
RETRY_TRANSIENT_ONLY = retry(
    reraise=True,
    stop=stop_after_attempt(5),
    wait=wait_exponential_jitter(initial=2, max=30),
    retry=lambda e: is_transient_error(e)
)

# Wrapper to apply to async LangChain invoke calls
async def robust_invoke(chain, input_data):
    @RETRY_DECORATOR
    async def _invoke():
        return await chain.ainvoke(input_data)
    
    return await _invoke()
