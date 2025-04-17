import os
import json
from google.cloud import storage
from gemini import describe_image


storage_client = storage.Client()
BUCKET_NAME = "lmattos-project2"

bucket = storage_client.bucket(BUCKET_NAME)

from flask import Flask, request, redirect, send_file
app = Flask(__name__)

os.makedirs('files', exist_ok = True)

@app.get("/")
def index():
    """Index page"""
    #who = request.args.get("who", default="World")

    #bucket = storage_client.get_bucket(BUCKET_NAME)
    #content_list = list(bucket.list_blobs(prefix=f"{BUCKET_PATH}/"))
    blobs = storage_client.list_blobs(BUCKET_NAME)
    return f'''
<form method="post" enctype="multipart/form-data" action="/upload" method="post">
  <div>
    <label for="file">Choose file to upload</label>
    <input type="file" id="file" name="form_file" accept="image/jpeg"/>
  </div>
  <div>
    <button>Submit</button>
  </div>
  <div>
    {list_files()}
  </div>
</form>
    '''

@app.route('/upload', methods=["POST"])
def upload():
    #save locally
    file = request.files["form_file"]
    file.save(f"./files/{file.filename}")
    
    #upload to bucket
    blob = bucket.blob(file.filename)
    blob.upload_from_filename(f"./files/{file.filename}")

    #generate description file
    description = describe_image(f"./files/{file.filename}")
    base, _ = os.path.splitext(file.filename)
    with open(f"./files/{base}.json", "w") as outfile:
      json.dump(description, outfile)

    #upload json
    blob = bucket.blob(f"{base}.json")
    blob.upload_from_filename(f"./files/{base}.json")

    return redirect("/")

@app.route('/files')
def list_files():
    # files = os.listdir("./files")
    # images = []
    # for file in files:
    #     if file.lower().endswith(".jpeg") or file.lower().endswith(".jpg"):
    #         images.append(file)
    blobs = storage_client.list_blobs(BUCKET_NAME)
    images = []
    for blob in blobs:
        if blob.name.lower().endswith(".jpeg") or blob.name.lower().endswith(".jpg"):
            images.append(f"{blob.name}")
    
    html = "<ul>"
    for i in images:
        html += f"<li><a href={"/imageview/" + i}>{i}</a></li>"
    html += "</ul>"
    print(html)
    return html

@app.route('/files/<filename>')
def get_file(filename):
    bucket.blob(filename).download_to_filename(f"./files/{filename}")
    return send_file(f"./files/{filename}")

@app.route('/imageview/<filename>')
def display_image(filename):
    base, _ = os.path.splitext(filename)
    bucket.blob(f"{base}.json").download_to_filename(f"./files/{base}.json")
    with open(f"./files/{base}.json", "r") as openfile:
      json_object = json.load(openfile)


    html = f"<h1>{json_object["title"]}</h1>"
    html += f"<h3>{json_object["description"]}</h3>"
    html += f"<img src=/files/{filename} alt=\"{json_object["title"]}\">"
    return html
    

if __name__ == "__main__":
    # Development only: run "python main.py" and open http://localhost:8080
    # When deploying to Cloud Run, a production-grade WSGI HTTP server,
    # such as Gunicorn, will serve the app.
    app.run(host="localhost", port=8080, debug=True)
