from openai import OpenAI
from package.common import read_api_key


openai_token = read_api_key("OPENAI_API_KEY")
client = OpenAI(
    api_key=openai_token
)

logo = "Travel agent telegram bot logo. Keep the logo simple so that the outlines is visible even in a small picture. " \
         "Draw only logo. On logo draw the smiling retro-robot with black glasses, Hawaiian shirt, hat. Use bright colors, blue, yellow. "\
         "Draw the sea and palm trees in the background. General Theme must be sunny. Design must be vector like"


response = client.images.generate(
  model="dall-e-3",
  prompt="make a background realistic 3d design object with thematic of modern smart industrial refrigerator with one slot. Add qr-code ilustrations. Make it like a poster of the startup",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)