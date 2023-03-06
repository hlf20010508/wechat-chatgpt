import openai
import os

openai.api_key = os.environ['api_key']

def reply(message):
  result = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": message}]
  )
  return result['choices'][0]['message']['content'].strip()