from langchain_groq import ChatGroq
from langchain_openrouter import ChatOpenRouter
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter

load_dotenv()

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.2,
    check_every_n_seconds=0.1,
    max_bucket_size=1
)

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=rate_limiter,
    request_timeout=60,
    max_retries = 3,
    temperature=0,   
)

fallback_llm = ChatOpenRouter(
    model="meta-llama/llama-3.3-70b-instruct",
    temperature=0
)
