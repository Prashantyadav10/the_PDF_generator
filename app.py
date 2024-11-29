from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from fpdf import FPDF
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
# Default settings
app.config['UPLOAD_FOLDER'] = 'generated_pdfs'
app.config['STATIC_FOLDER'] = 'static'

# Ensure static files are served correctly
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.config['STATIC_FOLDER'], filename)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Mock user data (replace with real authentication in production)
users = {"u@example.com": "pass"}

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Directory to save PDFs
PDF_DIR = 'generated_pdfs'
os.makedirs(PDF_DIR, exist_ok=True)

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email] == password:
            user = User(email)
            login_user(user)
            return redirect(url_for('home'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/generate-pdf', methods=['POST'])
@login_required
def generate_pdf():
    try:
        # Extract input from the form
        text = request.form.get('text')
        template = request.form.get('template')
        image = request.files.get('image')

        # Validate input
        if not text:
            return jsonify({"error": "Text is required"}), 400
        if not image:
            return jsonify({"error": "Image is required"}), 400

        # Initialize FPDF
        pdf = FPDF()
        pdf.add_page()

        # Set a Unicode font
        font_path = os.path.join(os.getcwd(), "fonts", "DejaVuSans.ttf")
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.set_font('DejaVu', size=12)

        # Add text to the PDF
        pdf.multi_cell(0, 10, text)

        # Save and add image
        image_path = os.path.join(PDF_DIR, "temp_image.jpg")
        image.save(image_path)
        pdf.image(image_path, x=10, y=pdf.get_y() + 10, w=100)

        # Save PDF
        pdf_filename = f"output_{session.get('user_id', 'user')}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        pdf.output(pdf_path)

        return jsonify({"pdf_url": f"/download/{pdf_filename}"})
    except Exception as e:
        # Log the error for debugging
        print("Error occurred while generating PDF:", str(e))
        return jsonify({"error": "Failed to generate PDF"}), 500

@app.route('/download/<filename>')
@login_required
def download_pdf(filename):
    try:
        return send_from_directory(PDF_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)