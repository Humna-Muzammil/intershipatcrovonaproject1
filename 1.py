from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
import os

load_dotenv()

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

conversation = []

document_text = ""


def read_document(file):
    filename = file.filename.lower()

    if filename.endswith(".txt"):
        return file.read().decode("utf-8")

    elif filename.endswith(".pdf"):
        reader = PdfReader(file)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    elif filename.endswith(".docx"):
        doc = Document(file)

        text = ""

        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        return text

    return ""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    user_message = request.json.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Please enter a message."})

    conversation.append({
        "role": "user",
        "content": user_message
    })

    system_message = """
You are an AI Productivity Assistant.

Help the user with:
- Questions
- Studying
- Summaries
- Writing
- Programming
- Productivity
- Planning

Give clear and useful answers.
Remember the previous conversation and understand follow-up questions.
"""

    messages = [
        {
            "role": "system",
            "content": system_message
        }
    ]

    messages.extend(conversation)

    if document_text:

        messages.append({
            "role": "system",
            "content": f"""
The user has uploaded a document.

Use the following document when answering questions
related to it:

--- DOCUMENT ---
{document_text}
--- END DOCUMENT ---
"""
        })

    try:

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        answer = response.choices[0].message.content

        conversation.append({
            "role": "assistant",
            "content": answer
        })

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


@app.route("/upload", methods=["POST"])
def upload():

    global document_text

    if "file" not in request.files:
        return jsonify({
            "error": "No file uploaded."
        })

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "error": "Please select a file."
        })

    try:

        document_text = read_document(file)

        if not document_text:
            return jsonify({
                "error": "Could not extract text from this document."
            })

        return jsonify({
            "message": f"{file.filename} uploaded successfully.",
            "characters": len(document_text)
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


@app.route("/clear", methods=["POST"])
def clear():

    global conversation
    global document_text

    conversation = []
    document_text = ""

    return jsonify({
        "message": "Conversation cleared."
    })


if __name__ == "__main__":
    app.run(debug=True)