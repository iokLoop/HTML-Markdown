from flask import Flask, render_template, request, jsonify
import os
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.lexers import get_lexer_by_name, get_all_lexers
from pygments.formatters import HtmlFormatter

app = Flask(__name__)

# Función personalizada para resaltar bloques de código
def pygments_highlight(code, lang):
    try:
        lexer = get_lexer_by_name(lang, stripall=True) if lang in get_all_lexers() else get_lexer_by_name("text", stripall=True)
        # lexer = get_lexer_by_name(lang, stripall=True)
    except Exception:
        lexer = get_lexer_by_name("text", stripall=True)
    formatter = HtmlFormatter()
    return highlight(code, lexer, formatter)

# MarkdownIt con resaltado personalizado
def markdown_with_syntax_highlighting(md_input):
    md = MarkdownIt("gfm-like")

    def custom_fence_renderer(tokens, idx, options, env, _renderer):
        token = tokens[idx]
        lang = token.info.strip() or "text"
        code = token.content
        return pygments_highlight(code, lang)

    md.add_render_rule("fence", custom_fence_renderer)
    return md.render(md_input)

@app.route('/', methods=['GET', 'POST'])
def editor():
    rendered_text = ""
    file_path = ""
    
    if request.method == 'POST':
        # Obtener el path del archivo desde el formulario
        file_path = request.form.get('file_path')
        print(f"Ruta del archivo recibida: {file_path}")  # Debug aquí
        
        if file_path:
            try:
                # Comprobar si la ruta del archivo es válida
                if not os.path.exists(file_path):
                    # Loggear el error
                    app.logger.error(f"Invalid file path: {file_path}")
                    rendered_text = "Error: La ruta del archivo no es válida o no existe."
                elif os.path.exists(file_path):
                    # Leer el archivo Markdown
                    with open(file_path, 'r') as file:
                        markdown_input = file.read()
                        print(f"Contenido del archivo Markdown: {markdown_input}")  # Debug aquí
                    
                    # Convertir Markdown a HTML
                    rendered_text = markdown_with_syntax_highlighting(markdown_input)
                    print(f"Texto renderizado: {rendered_text}")  # Para debug
                    
            except Exception as e:
                rendered_text = f"Error al leer el archivo: {e}"

    # Renderizar la página, ya sea con o sin el texto renderizado
    return render_template("Markdown-Reader.html", rendered_text=rendered_text, file_path=file_path)

@app.route('/update_preview', methods=['POST'])
def update_preview():
    # Imprime los datos recibidos para depuración
    data = request.get_json()
    print(f"Datos recibidos por AJAX: {data}")
    
    file_path = data.get('file_path', "")
    
    if not file_path:
        app.logger.error("No file path provided in AJAX request.")

    elif file_path and os.path.exists(file_path):
        try:
            # Leer el archivo Markdown
            with open(file_path, 'r') as file:
                markdown_input = file.read()
                
            # Convertir Markdown a HTML
            rendered_text = markdown_with_syntax_highlighting(markdown_input)
            print(f"Texto renderizado por AJAX: {rendered_text}")  # Para depuración
            return rendered_text  # Regresar solo el HTML del contenido renderizado
        except Exception as e:
            print(f"Error al leer el archivo: {e}")
            return f"Error al leer el archivo: {e}", 500
    else:
        print("Error: La ruta del archivo no es válida o no existe.")
        return "Error: La ruta del archivo no es válida o no existe.", 400

if __name__ == '__main__':
    app.run(debug=True)
