from flask import Flask, request, jsonify
from flask_cors import CORS
import os, tempfile
import PyPDF2
import openai
from sentence_transformers import SentenceTransformer
import faiss

app = Flask(__name__)
CORS(app)
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load the embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize FAISS index
embedding_size = 384  # Adjust based on your model
index = faiss.IndexFlatL2(embedding_size)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''.join(page.extract_text() for page in reader.pages)
    return text

# Root route
@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Extract text from PDF
    text_data = extract_text_from_pdf(file_path)

    # Create embeddings
    embeddings = model.encode([text_data])
    index.add(embeddings)

    return jsonify({"message": "File uploaded and processed"}), 200

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    query = data['query']

    # Create embedding for the query
    query_embedding = model.encode([query])

    # Perform nearest neighbor search
    D, I = index.search(query_embedding, k=1)

    # Retrieve relevant document
    relevant_text = " ".join([extracted_texts[i] for i in I[0]])  # Assuming you store extracted texts in a list

    # Generate a response using OpenAI GPT
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Answer this query: {query} based on this document: {relevant_text}",
        max_tokens=150
    )

    return jsonify({"answer": response['choices'][0]['text']}), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)
