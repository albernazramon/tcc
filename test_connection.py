import ollama

response = ollama.chat(model='gemma3', messages=[
  {
    'role': 'user',
    'content': 'Explain the difference between INNER JOIN and LEFT JOIN.',
  },
])
print(response['message']['content'])