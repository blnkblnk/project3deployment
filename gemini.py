import os
import google.generativeai as genai
import json

genai.configure(api_key=os.environ['GEMINI_API'])

generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "application/json",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
#   generation_config=generation_config,
  # safety_settings = Adjust safety settings
  # See https://ai.google.dev/gemini-api/docs/safety-settings
)

PROMPT = """respond exactly in this format. do not use markdown.
{
   "title" : "PLACE THE GENERATED TITLE HERE",
   "description" : "PLACE THE GENERATED DESCRIPTION HERE"
}"""

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  # print(file)
  return file

def describe_image(path, prompt=PROMPT):
  response = model.generate_content(
    [upload_to_gemini(path, mime_type="image/jpeg"), "\n\n", prompt]
  )
  json_object = {
    'title': 'Default Title',
    'description': 'Default Description'
  }
  try:
    json_object = json.loads(response.text)
  except Exception as e:
    print(f"An error in decoding json occurred: {e}")
    print(f"Attempted to decode: {response.text}")
  return json_object
  

if __name__ == "__main__":
  print(describe_image('files/image1.jpg'))
