import os
import openai

api_key = open('resource\ChatGPT_api_key.txt').read()
openai.api_key = api_key
openai.organization = "org-J0PWE1RbQlGThBFfHT3iYmgO"
# endpoint = "https://api.openai.com/v1/gpt-3.5/answers"
endpoint = 'https://api.openai.com/v1/chat/completions'

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
}

messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
]

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.7,
    max_tokens=50
)

print(response)