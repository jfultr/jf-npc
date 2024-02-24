from openai import OpenAI
from package.common import read_api_key


openai_token = read_api_key("OPENAI_API_KEY")
client = OpenAI(
    api_key=openai_token
)

logo = "Travel agent telegram bot logo. Keep the logo simple so that the outlines is visible even in a small picture. " \
         "Draw only logo. On logo draw the smiling retro-robot with black glasses, Hawaiian shirt, hat. Use bright colors, blue, yellow. "\
         "Draw the sea and palm trees in the background. General Theme must be sunny. Design must be vector like"

_prompt = """
Iam 3d artist, making a graphical design for single-door industrial refrigerator.
give me some inspiring stylish references for side panel. use theme of degital starup with texts and qr-code
make the design bright and colorfull with huge outlines. the disgn without small details
""" 


_prompt = """
it startup poster with 3d arts. related with street food. theme degital starup with texts and qr-codes.
catchy colorfull design. with amount of black color and japan anime style. ratio 1 width to 2 high  
"""

_prompt = """
a few clouds drawed blue and white by сhalk
"""

response = client.images.generate(
  model="dall-e-3",
  prompt=_prompt,
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url
print(image_url)