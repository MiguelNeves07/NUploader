import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Configuração do SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # Limite de 100MB

# Inicializar o banco de dados
db = SQLAlchemy(app)

# Criação do diretório de uploads, caso não exista
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Modelo de vídeo para o banco de dados
class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(100), nullable=False)

# Função para inicializar o banco de dados
def init_db():
    db.create_all()

@app.route('/')
def index():
    # Recuperar todos os vídeos do banco de dados
    videos = Video.query.all()
    return render_template('index.html', videos=videos)

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return 'Nenhum arquivo selecionado', 400

    video = request.files['video']

    if video.filename == '':
        return 'Nenhum arquivo selecionado', 400

    if video:
        # Salvar o vídeo no diretório de uploads
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video.filename)
        video.save(video_path)

        # Salvar o nome do vídeo no banco de dados
        new_video = Video(filename=video.filename)
        db.session.add(new_video)
        db.session.commit()

        return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_video(filename):
    # Enviar o arquivo de vídeo diretamente da pasta de uploads
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Inicializar o banco de dados
with app.app_context():
    init_db()

if __name__ == '__main__':
    # Usar a porta dinâmica do Render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
