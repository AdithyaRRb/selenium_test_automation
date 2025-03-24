from flask import Flask, request, jsonify, send_file
import subprocess

app = Flask(__name__)

SCRIPT_PATH = "received_script.py"

# ✅ Route to receive and save the script
@app.route('/view_script', methods=['POST'])
def upload_script():
    data = request.json
    script_content = data.get("script", "")

    if not script_content:
        return jsonify({"error": "No script content received"}), 400

    with open(SCRIPT_PATH, "w", encoding="utf-8") as file:
        file.write(script_content)

    return jsonify({"message": "Script received successfully!"})

# ✅ Route to view the script
@app.route('/view_script', methods=['GET'])
def view_script():
    try:
        with open(SCRIPT_PATH, "r", encoding="utf-8") as file:
            content = file.read()
        return f"<pre>{content}</pre>", 200
    except FileNotFoundError:
        return "No script received yet.", 404

# ✅ Route to download the script
@app.route('/download_script', methods=['GET'])
def download_script():
    return send_file(SCRIPT_PATH, as_attachment=True)

# ✅ Route to run the script automatically
@app.route('/run_script', methods=['POST'])
def run_script():
    try:
        # Execute the script with Python
        process = subprocess.Popen(["python", SCRIPT_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = process.communicate()

        if process.returncode == 0:
            return jsonify({"message": "Script executed successfully!", "output": output.decode()}), 200
        else:
            return jsonify({"error": "Script execution failed!", "details": error.decode()}), 500

    except FileNotFoundError:
        return jsonify({"error": "No script found to run!"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
