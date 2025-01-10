from flask import Flask, render_template, request, jsonify
from markdown_it import MarkdownIt

app = Flask(__name__)
md = MarkdownIt("gfm-like")

@app.route("/", methods=["GET", "POST"])
def editor():
    if request.method == "POST":
        markdown_input = request.form["markdown_input"]
        
        rendered_text = md.render(markdown_input)  # Convert Markdown to HTML
        return rendered_text  # Retorn pure HTML
    return render_template("Markdown-Editor.html")  # Render the html template

if __name__ == "__main__":
    app.run(debug=True)