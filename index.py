from flask import Flask, render_template_string, request, session
import difflib, json, os

app = Flask(__name__)
app.secret_key = "secret123"  # session ke liye

DATA_FILE = "qa_data.json"
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        qa_data = json.load(f)
else:
    qa_data = {}

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(qa_data, f, ensure_ascii=False, indent=2)

HTML = """
<!DOCTYPE html>
<html><body>
<h2>Chatbot</h2>
<div style="border:1px solid #ccc; padding:10px; width:400px; height:250px; overflow:auto;">
{% for m in chat %}
<p><b>You:</b> {{m[0]}}</p>
<p><b>Bot:</b> {{m[1]}}</p>
<hr>
{% endfor %}
</div>

<form method="POST">
<input type="text" name="message" placeholder="Type a message" style="width:300px;">
<button type="submit">Send</button>
</form>
</body></html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if "chat" not in session:
        session["chat"] = []
    if "teach_mode" not in session:
        session["teach_mode"] = None
    if "pending_question" not in session:
        session["pending_question"] = None

    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        reply = ""

        # Teach mode handling
        if msg.lower() == "teach":
            session["teach_mode"] = "ask_question"
            reply = "Enter question:"
        elif session["teach_mode"] == "ask_question":
            session["pending_question"] = msg
            session["teach_mode"] = "ask_answer"
            reply = "Enter answer:"
        elif session["teach_mode"] == "ask_answer":
            q = session["pending_question"]
            a = msg
            qa_data[q] = a
            save_data()
            reply = f"Learned successfully! ('{q}' → '{a}')"
            session["teach_mode"] = None
            session["pending_question"] = None
        else:
            # Normal Q&A mode
            match = difflib.get_close_matches(msg, list(qa_data.keys()), n=1, cutoff=0.6)
            if match:
                reply = qa_data[match[0]]
            else:
                reply = "Mujhe ye sawal nahi aata. Agar sikhana hai to 'teach' likho."

        # update chat history
        session["chat"].append((msg, reply))
        session.modified = True

    return render_template_string(HTML, chat=session["chat"])

if __name__ == "__main__":
    app.run(debug=True)
