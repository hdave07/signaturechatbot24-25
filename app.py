from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import fitz


app = Flask(__name__)
CORS(app)


# Load PDF content
def extract_pdf_text(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        text += page.get_text("text") + "\n"
    return text
    

pdf_path = "Signature_ Emma Info PDF.pdf"
pdf_content = extract_pdf_text(pdf_path)

#function  to retrieve the content based on key words
def retrieve_relavent_text(user_query, pdf_text):
    user_keywords = user_query.lower().split()
    relavent_sentences = []

    for line in pdf_text.split("\n"):
        if any(keyword in line.lower() for keyword in user_keywords):
            relavent_sentences.append(line)

    return " ".join(relavent_sentences[:15]) #--> limits the #of relevent sentences returned

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/chatbot", methods=["POST"])
def chatbot():
    user_query = request.json.get("query")

    relavent_text = retrieve_relavent_text(user_query, pdf_content)

    ollama_payload = {
        "model": "llama3",
        "prompt": f"Question: {user_query}\nDocument Info: {relavent_text}\nAnswer concisely with the most relavent information from the user question.",
        "stream": False
    }
    
    response = requests.post("http://localhost:11434/api/generate", json=ollama_payload).json()
    chatbot_reply = response.get("response", "Sorry, I couldn't generate a response.")

    return jsonify({"reply": chatbot_reply})
    
if __name__ == "__main__":
    app.run(debug=True)