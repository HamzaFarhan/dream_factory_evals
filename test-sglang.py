import openai

# Configure the client to point to your SGLang Docker container
client = openai.OpenAI(
    base_url="http://34.121.101.35:30000/v1",  # Default SGLang Docker port
    api_key="EMPTY",  # SGLang doesn't require an API key
)

# Test a simple completion
response = client.chat.completions.create(
    model="default",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Tell me a short joke about Docker."},
    ],
    temperature=0.7,
    max_tokens=50,
)

print("Response from SGLang Docker container:")
print(response.choices[0].message.content)

# Test streaming
print("\nTesting streaming response:")
stream = client.chat.completions.create(
    model="default",
    messages=[{"role": "user", "content": "Explain Docker in one sentence."}],
    stream=True,
    max_tokens=30,
)

for chunk in stream:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)
print()
