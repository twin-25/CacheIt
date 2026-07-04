from prometheus_client import Counter, Histogram


cache_hits_total = Counter("cacheit_hits_total", "Total cache hits")
cache_misses_total = Counter("cacheit_misses_total", "Total cache misses")
llm_duration_seconds = Histogram("cacheit_llm_duration_seconds", "LLM call duration in seconds")