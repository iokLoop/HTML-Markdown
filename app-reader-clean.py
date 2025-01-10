from flask import Flask, render_template, request, jsonify
import os
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter
from mdit_py_plugins.tasklists import tasklists_plugin

app = Flask(__name__)

def pygments_highlight(code, lang):
    try:
        available_lexers = [lexer[0].casefold() for lexer in get_all_lexers()]
        if lang.casefold() in available_lexers:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = get_lexer_by_name("text", stripall=True)
    except Exception:
        lexer = get_lexer_by_name("text", stripall=True)

    formatter = HtmlFormatter(style='gruvbox-dark', linenos=True)
    formatter.get_style_defs('.highlight')

    return highlight(code, lexer, formatter)

def markdown_with_syntax_highlighting(md_input):

    md = MarkdownIt("commonmark").enable('table').use(tasklists_plugin)

    def custom_fence_renderer(tokens, idx, options, env):

        token = tokens[idx]
        lang = token.info.strip() or "text"
        code = token.content

        return pygments_highlight(code, lang)
    
    md.renderer.rules['fence'] = custom_fence_renderer
    return md.render(md_input)

@app.route('/', methods=['GET', 'POST'])
def editor():

    rendered_text = ""
    file_path = ""
    
    if request.method == 'POST':
        file_path = request.form.get('file_path')
        
        if file_path:
            try:
                if not os.path.exists(file_path):
                    app.logger.error(f"Invalid file path: {file_path}")
                    rendered_text = "Error: The file path is invalid or does not exist."
                else:
                    with open(file_path, 'r') as file:
                        markdown_input = file.read()

                    rendered_text = markdown_with_syntax_highlighting(markdown_input)
                    
            except Exception as e:
                rendered_text = f"Error reading the file: {e}"

    return render_template("Markdown-Reader2.html", rendered_text=rendered_text, file_path=file_path)

@app.route('/update_preview', methods=['POST'])
def update_preview():

    data = request.get_json()
    print(f"Data received via AJAX: {data}")
    file_path = data.get('file_path', "")
    
    if not file_path:
        app.logger.error("No file path provided in AJAX request.")
        
    elif file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as file:
                markdown_input = file.read()
                
            rendered_text = markdown_with_syntax_highlighting(markdown_input)

            return rendered_text
        
        except Exception as e:
            print(f"Error reading the file: {e}")
            return f"Error reading the file: {e}", 500
    else:
        print("Error: The file path is invalid or does not exist.")
        return "Error: The file path is invalid or does not exist.", 400

if __name__ == '__main__':
    app.run(debug=True)