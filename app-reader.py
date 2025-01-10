from flask import Flask, render_template, request, jsonify
import os
from markdown_it import MarkdownIt

app = Flask(__name__)
md = MarkdownIt("gfm-like")

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
                if os.path.exists(file_path):
                    # Leer el archivo Markdown
                    with open(file_path, 'r') as file:
                        markdown_input = file.read()
                        print(f"Contenido del archivo Markdown: {markdown_input}")  # Debug aquí
                    
                    # Convertir Markdown a HTML
                    rendered_text = md.render(markdown_input)
                    print(f"Texto renderizado: {rendered_text}")  # Para debug
                else:
                    rendered_text = "Error: La ruta del archivo no es válida o no existe."
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
    
    if file_path and os.path.exists(file_path):
        try:
            # Leer el archivo Markdown
            with open(file_path, 'r') as file:
                markdown_input = file.read()
                
            # Convertir Markdown a HTML
            rendered_text = md.render(markdown_input)
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
