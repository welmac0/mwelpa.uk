from flask import Flask, render_template, send_file
from flask_bootstrap import Bootstrap
import json
import os
from datetime import datetime, date 
import yaml
import marko


app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
Bootstrap(app)


def get_content():
    with open("static/files/source.json") as content:
        content = json.loads(content.read())

    return content


@app.route('/')
def home():
    return render_template("index.html", content=get_content())

# gpt
POSTS_DIR = "static/posts/"

def parse_markdown_post(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    metadata = {}
    markdown_content = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            front_matter_str = parts[1]
            markdown_content = parts[2]
            metadata = yaml.safe_load(front_matter_str)
        else:
            metadata = {}
            markdown_content = content
    else:
        metadata = {}
        markdown_content = content

    # --- Kluczowa modyfikacja tutaj ---
    # Konwertuj 'date' na obiekt datetime.date
    raw_date = metadata.get('date')
    if isinstance(raw_date, str):
        try:
            # Próba sparsowania stringa jako daty (np. 'YYYY-MM-DD')
            metadata['date'] = datetime.strptime(raw_date, '%Y-%m-%d').date()
        except ValueError:
            # Jeśli string nie jest poprawnym formatem daty, ustaw None lub domyślną datę
            metadata['date'] = None # Używamy None, a potem obsłużymy to w contents()
            #print(f"Ostrzeżenie: Nieprawidłowy format daty w pliku {filepath}: {raw_date}. Ustawiono None.")
    elif not isinstance(raw_date, (date, datetime)):
        # Jeśli data nie jest ani stringiem, ani obiektem daty/datetime (np. jest None z YAML)
        metadata['date'] = None # Ustawiamy None
    # Jeśli raw_date jest już obiektem date/datetime, pozostaje bez zmian
    # --- Koniec modyfikacji ---
    html_content = marko.convert(markdown_content)
    return metadata, html_content

@app.route('/blog/<slug>')
def blog_post(slug):
    filepath = os.path.join(POSTS_DIR, f'{slug}.md')
    if not os.path.exists(filepath):
        return("404 err") # Zwróć błąd 404, jeśli plik nie istnieje

    metadata, html_content = parse_markdown_post(filepath)
    #print(html_content)

    return render_template('blog_post.html',
                           title=metadata.get('title', slug.replace('-', ' ').title()),
                           date=metadata.get('date', 'Brak daty'),
                           author=metadata.get('author', 'Nieznany autor'),
                           content=html_content)

@app.route('/contents')
def contents():
    posts = []
    
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(POSTS_DIR, filename)
            slug = os.path.splitext(filename)[0]
            metadata, _ = parse_markdown_post(filepath)
            
            post_date = metadata.get('date')
            # Jeśli data jest None (bo nie było jej w metadanych lub była błędna),
            # przypisz bardzo wczesną datę, aby posty bez daty były na końcu po sortowaniu malejąco
            if post_date is None:
                post_date = date(1900, 1, 1) # Użyj dowolnej bardzo wczesnej daty
            
            posts.append({
                'slug': slug,
                'title': metadata.get('title', slug.replace('-', ' ').title()),
                'date': post_date, # Teraz 'date' jest zawsze obiektem date
                'description': metadata.get('description', 'Brak opisu.'),
                'author': metadata.get('author', 'Nieznany autor')
            })

    # Sortuj posty po dacie (najnowsze na górze)
    # Teraz sortowanie jest bezpieczne, bo wszystkie daty są obiektami date
    posts.sort(key=lambda x: x['date'], reverse=True) 
    
    return render_template("contents.html", posts=posts)

# end of gpt

@app.route('/iwantresume')
def give_resume():
    file = f'static/files/resume_mWelpa.pdf'
    return send_file(file, as_attachment=True)

@app.errorhandler(404)
def page_not_found(e):
    return "Page not found :( <a href='/'>Go back home</a>", 404

if __name__ == "__main__":
    app.run(debug=True, port=5001)




