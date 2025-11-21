import os

AGENT_MAX_RETRIES = int(os.getenv("AGENT_MAX_RETRIES", "2"))
AGENT_STEP_TIMEOUT_SECONDS = float(
    os.getenv("AGENT_STEP_TIMEOUT_SECONDS", "30"))
