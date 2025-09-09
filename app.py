from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lectures (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            audio_file TEXT,
            slide_file TEXT,
            video_file TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lectures ORDER BY id DESC")
    lectures = cursor.fetchall()
    conn.close()
    
    # Convert to dicts
    lectures = [{
        'id': l[0],
        'title': l[1],
        'description': l[2],
        'audio_file': l[3],
        'slide_file': l[4],
        'video_file': l[5]
    } for l in lectures]

    return render_template('index.html', lectures=lectures)


@app.route('/virtual_classroom/<int:lecture_id>')
def virtual_classroom(lecture_id):
    # Load lecture data if needed
    return render_template('virtual_classroom.html', lecture_id=lecture_id)



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        audio = request.files['audio_file']
        slides = request.files['slide_file']
        video = request.files['video_file']

        # Generate safe filenames
        audio_filename = f"{title.replace(' ', '_')}_audio.mp3"
        slide_filename = f"{title.replace(' ', '_')}_slides.pdf"
        video_filename = f"{title.replace(' ', '_')}_video.mp4"

        # Save files
        audio.save(os.path.join(UPLOAD_FOLDER, audio_filename))
        slides.save(os.path.join(UPLOAD_FOLDER, slide_filename))
        video.save(os.path.join(UPLOAD_FOLDER, video_filename))

        # Store in database
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO lectures (title, description, audio_file, slide_file, video_file)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, audio_filename, slide_filename, video_filename))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('upload.html')




@app.route('/lecture/<int:lecture_id>')
def lecture(lecture_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lectures WHERE id = ?", (lecture_id,))
    lec = cursor.fetchone()
    conn.close()

    if lec:
        # Convert tuple to dictionary for template
        lecture = {
            'id': lec[0],
            'title': lec[1],
            'description': lec[2],
            'audio_file': lec[3],
            'slide_file': lec[4],
            'video_file': lec[5]
        }
        return render_template('lecture.html', lecture=lecture)
    return "Lecture not found", 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
