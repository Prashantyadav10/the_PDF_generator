from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from fpdf import FPDF
import os
import time

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
            session['user_id'] = email  # Store the user ID in session
            return redirect(url_for('home'))
        return "Invalid credentials", 401
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)  # Clear session data
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

        # Initialize FPDF
        pdf = FPDF()
        pdf.add_page()

        # Set font based on the selected template
        font_path = os.path.join(os.getcwd(), "fonts", "DejaVuSans.ttf")
        try:
            pdf.add_font('DejaVu', '', font_path, uni=True)
        except Exception as e:
            print(f"Font loading error: {e}")

        if template == 'Times New Roman':
            pdf.set_font('Times', size=12)
            pdf.set_text_color(50, 50, 255)  # Blue text for modern
        elif template == 'Arial':
            pdf.set_font('Arial', size=12)
            pdf.set_text_color(0, 0, 0)  # Black text for classic
        else:  # Default template
            pdf.set_font('DejaVu', size=12)
            pdf.set_text_color(0, 0, 0)  # Black text for default

        # Process text line by line
        lines = text.split('\n')
        default_font = ('Arial', '', 12)  # Default font

        for line in lines:
            if line.startswith('/H'):  # Heading
                pdf.set_font('Times', style='BU', size=14)
                pdf.multi_cell(0, 10, line[2:].strip())  # Remove symbol and add text
            elif line.startswith('/S'):  # Subheading
                pdf.set_font('Times', style='B', size=12)
                pdf.multi_cell(0, 10, line[2:].strip())  # Remove symbol and add text
            else:  # Regular text
                pdf.set_font(*default_font)
                pdf.multi_cell(0, 10, line.strip())

        # Handle image upload        
        allowed_extensions = {'.png', '.jpg', '.jpeg'}
        if image:
            filename = image.filename
            file_ext = os.path.splitext(filename)[1].lower()  # Extract extension and make it lowercase

            if file_ext in allowed_extensions:
                # Generate a unique filename using timestamp and user ID
                unique_filename = f"temp_image_{int(time.time())}_{session.get('user_id', 'user')}{file_ext}"
                image_path = os.path.join(PDF_DIR, unique_filename)
                image.save(image_path)

                # Add the image to the PDF
                pdf.image(image_path, x=10, y=pdf.get_y() + 10, w=100)
            else:
                return jsonify({"error": "Invalid image format. Allowed formats are PNG, JPG, JPEG."}), 400

        # Save the PDF
        pdf_filename = f"output_{session.get('user_id', 'user')}.pdf"
        pdf_path = os.path.join(PDF_DIR, pdf_filename)
        pdf.output(pdf_path)

        # Return the download link
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
