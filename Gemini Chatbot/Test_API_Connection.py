import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# 🔐 Set your API key here
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the model for the free tier
model = genai.GenerativeModel(model_name='models/gemini-2.5-pro-exp-03-25')

# Generate content
response = model.generate_content("What is AI?")
print(response.text)
