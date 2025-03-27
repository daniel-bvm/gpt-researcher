from nikolasigmoid/py-agent-infra:latest

copy app app
copy gpt_researcher gpt_researcher
copy requirements.txt requirements.txt

run python -m pip install --no-cache-dir -r requirements.txt && rm -rf requirements.txt 

env ETERNALAI_MCP_PROXY_URL="https://agent-service-client.dev.eternalai.org/execution"
env PROXY_SCOPE="*api.tavily.com*"
env RETRIEVER="tavily"

env FAST_LLM="openai:$LLM_MODEL_ID"
env SMART_LLM="openai:$LLM_MODEL_ID"
env STRATEGIC_LLM="openai:$LLM_MODEL_ID"