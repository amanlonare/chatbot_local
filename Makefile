install:
	pip install -e .

clean:
	rm -rf .eggs __pycache__ .pytest_cache src/__pycache__ src/database/__pycache__ \
	src/llm/__pycache__ src/utils/__pycache__ src/templates/__pycache__ \
	chatbot_local.egg-info notebooks/__pycache__