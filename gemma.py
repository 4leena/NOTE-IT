import ollama



response = ollama.chat(
    model="gemma3:4b",  # Specify the model here
    messages=[
        {
            "role": "user",
            "content": "Hello, how are you?"
        }
    ]
)

print(response['message']['content'])