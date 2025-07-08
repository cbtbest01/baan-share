from flask import Flask, render_template
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

if __name__ == '__main__':
    # Port ที่ Render ให้ผ่าน environment variable PORT
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)