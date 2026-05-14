import json
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime
from urllib.parse import urlparse, parse_qs


ROOT = Path(__file__).parent


def yt_id(url: str) -> str:
    return parse_qs(urlparse(url).query).get("v", [""])[0]


def fmt_date(iso: str) -> str:
    try:
        return datetime.strptime(iso, "%Y-%m-%d").strftime("%d %b %Y")
    except ValueError:
        return iso


def load_content() -> dict:
    path = ROOT / "content.json"
    if not path.exists():
        return {"videos": [], "libros": []}
    return json.loads(path.read_text(encoding="utf-8"))


class MetaExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta      = {}
        self.title     = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self._in_title = True
        if tag == "meta":
            d = dict(attrs)
            name    = d.get("name", "")
            content = d.get("content", "")
            if name in ("description", "author",
                        "post:date", "post:category",
                        "post:tags", "post:status"):
                self.meta[name] = content

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def extract_post(path: Path) -> dict | None:
    parser = MetaExtractor()
    parser.feed(path.read_text(encoding="utf-8"))

    if parser.meta.get("post:status", "").strip().lower() != "published":
        return None

    raw_date = parser.meta.get("post:date", "").strip()
    try:
        date = datetime.strptime(raw_date, "%Y-%m-%d")
    except ValueError:
        return None

    tags_raw = parser.meta.get("post:tags", "")
    tags     = [t.strip() for t in tags_raw.split(",") if t.strip()]

    title = parser.title.strip()
    if " — " in title:
        title = title.split(" — ")[0].strip()

    return {
        "filename":    path.name,
        "title":       title,
        "date":        date,
        "date_str":    date.strftime("%d %b %Y"),
        "description": parser.meta.get("description", "").strip(),
        "category":    parser.meta.get("post:category", "").strip(),
        "tags":        tags,
    }


def collect_posts() -> list[dict]:
    blog_dir = ROOT / "blog"
    if not blog_dir.exists():
        return []
    posts = []
    for path in blog_dir.glob("*.html"):
        if path.name == "index.html":
            continue
        post = extract_post(path)
        if post:
            posts.append(post)
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


SHARED_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
    '  <link href="https://fonts.googleapis.com/css2?family=Lora:ital,'
    'wght@0,400;0,500;1,400&family=Playfair+Display:wght@700&family='
    'JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
)

FAVICON = (
    '<link rel="icon" href="data:image/svg+xml,'
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'>"
    "<text y='.9em' font-size='90'>🚀</text></svg>\">"
)

SHARED_CSS = """
    :root {
      --bg:        #F9F6F1;
      --bg-code:   #EFEBe4;
      --text:      #1C1917;
      --muted:     #6B6560;
      --border:    #D8D3CB;
      --accent:    #2A5C5A;
      --rule:      #C8C2B8;
      --font-body: 'Lora', Georgia, serif;
      --font-head: 'Playfair Display', 'Times New Roman', serif;
      --font-mono: 'JetBrains Mono', 'Courier New', monospace;
      --measure:   68ch;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    html {
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-body);
      font-size: 18px;
      line-height: 1.7;
      -webkit-font-smoothing: antialiased;
    }
    body { max-width: var(--measure); margin: 0 auto; padding: 0 1.5rem 6rem; }
    a { color: var(--accent); }
    footer.site-footer {
      margin-top: 4rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--rule);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem 1.75rem;
    }
    footer.site-footer a { color: var(--accent); text-decoration: none; }
    footer.site-footer a:hover { text-decoration: underline; }
    @media (max-width: 640px) { html { font-size: 16px; } }
"""

SHARED_FOOTER = """  <footer class="site-footer">
    <span>© César Uribe</span>
    <a href="mailto:cesaruribeperu@gmail.com">cesaruribeperu@gmail.com</a>
    <a href="https://www.youtube.com/@uribecesare" target="_blank" rel="noopener">YouTube</a>
    <a href="https://uribecesar.github.io">uribecesar.github.io</a>
  </footer>"""


def render_home(posts: list[dict], content: dict) -> str:
    videos = content.get("videos", [])
    libros = content.get("libros", [])

    video       = videos[0] if videos else None
    featured    = posts[0]  if posts  else None
    recent_list = posts[1:11] if len(posts) > 1 else []

    video_html = ""
    if video:
        vid      = yt_id(video.get("enlace", ""))
        vtitle   = video.get("titulo", "")
        vdate    = fmt_date(video.get("fecha_publicacion", ""))
        vlink    = video.get("enlace", "#")
        thumb    = f"https://img.youtube.com/vi/{vid}/maxresdefault.jpg" if vid else ""
        video_html = f"""
  <section class="video-block">
    <p class="section-label">Último video</p>
    <a class="video-card" href="{vlink}" target="_blank" rel="noopener">
      {"" if not thumb else f'<img src="{thumb}" alt="{vtitle}" loading="lazy">'}
      <div class="video-info">
        <span class="video-title">{vtitle}</span>
        <span class="video-date">{vdate}</span>
      </div>
    </a>
  </section>"""

    featured_html = ""
    if featured:
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in featured["tags"])
        featured_html = f"""
  <section class="featured-post">
    <p class="section-label">Último artículo</p>
    <div class="post-meta">
      <time datetime="{featured['date'].strftime('%Y-%m-%d')}">{featured['date_str']}</time>
      {f'<span class="category">{featured["category"]}</span>' if featured["category"] else ""}
    </div>
    <h2><a href="blog/{featured['filename']}">{featured['title']}</a></h2>
    {f'<p class="description">{featured["description"]}</p>' if featured["description"] else ""}
    {f'<div class="tags">{tags_html}</div>' if tags_html else ""}
  </section>"""

    recent_items = "".join(f"""
    <li>
      <span class="item-date">{p['date_str']}</span>
      <a href="blog/{p['filename']}">{p['title']}</a>
    </li>""" for p in recent_list)

    recent_html = ""
    if recent_items:
        recent_html = f"""
  <section class="recent-posts">
    <p class="section-label">Artículos recientes</p>
    <ul class="post-list">{recent_items}
    </ul>
    <a class="see-all" href="blog/">Ver todos →</a>
  </section>"""

    books_items = "".join(f"""
    <article class="book-card">
      <div class="book-header">
        <div>
          <h3><a href="{b.get('enlace','#')}" target="_blank" rel="noopener">{b.get('nombre_libro','')}</a></h3>
          <p class="book-author">{b.get('autor','')}</p>
        </div>
        <span class="book-year">{fmt_date(b.get('fecha_publicacion',''))[:8].strip()}</span>
      </div>
      {f'<p class="book-desc">{b.get("descripcion","")}</p>' if b.get("descripcion") else ""}
    </article>""" for b in libros)

    books_html = ""
    if books_items:
        books_html = f"""
  <section class="books-block">
    <p class="section-label">Libros recomendados</p>
    <div class="book-list">{books_items}
    </div>
  </section>"""

    now = datetime.now().strftime("%d %b %Y, %H:%M")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>César Uribe — Ingeniero de Sistemas &amp; Divulgador tecnológico</title>
  <meta name="description" content="Ingeniero de Sistemas especializado en automatización con IA para PYMEs. Cursos en Udemy, contenido en YouTube.">
  {FAVICON}
  {SHARED_FONTS}
  <style>{SHARED_CSS}
    .topbar {{
      display: flex;
      justify-content: flex-end;
      padding: 0.9rem 0;
      border-bottom: 0.5px solid var(--border);
      margin-bottom: 2.5rem;
    }}
    .btn {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      letter-spacing: 0.06em;
      padding: 0.4rem 1rem;
      border: 1px solid var(--accent);
      color: var(--accent);
      text-decoration: none;
      border-radius: 2px;
      transition: background 0.15s, color 0.15s;
    }}
    .btn:hover {{ background: var(--accent); color: var(--bg); }}
    .hero {{
      padding: 2rem 0 2rem;
      border-bottom: 1.5px solid var(--accent);
      margin-bottom: 3rem;
    }}
    .hero h1 {{
      font-family: var(--font-head);
      font-size: 2.6rem;
      font-weight: 700;
      line-height: 1.15;
      margin-bottom: 0.5rem;
    }}
    .hero .roles {{
      font-family: var(--font-mono);
      font-size: 0.78rem;
      letter-spacing: 0.08em;
      color: var(--accent);
      text-transform: uppercase;
      margin-bottom: 0.9rem;
    }}
    .hero .tagline {{
      font-size: 1.05rem;
      color: var(--muted);
      font-style: italic;
      margin-bottom: 1.25rem;
      max-width: 52ch;
      line-height: 1.6;
    }}
    .hero-links {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.5rem 1.25rem;
      font-family: var(--font-mono);
      font-size: 0.75rem;
    }}
    .hero-links a {{ color: var(--accent); text-decoration: none; }}
    .hero-links a:hover {{ text-decoration: underline; }}
    .section-label {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 1rem;
    }}
    .video-block {{ margin-bottom: 3rem; }}
    .video-card {{
      display: block;
      text-decoration: none;
      border: 1px solid var(--border);
      border-radius: 2px;
      overflow: hidden;
    }}
    .video-card:hover .video-title {{ color: var(--accent); }}
    .video-card img {{
      width: 100%;
      display: block;
      aspect-ratio: 16/9;
      object-fit: cover;
      filter: grayscale(10%) contrast(1.03);
    }}
    .video-info {{
      padding: 0.9rem 1rem;
      background: var(--bg-code);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 1rem;
    }}
    .video-title {{
      font-family: var(--font-head);
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text);
      line-height: 1.3;
    }}
    .video-date {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      white-space: nowrap;
    }}
    .featured-post {{
      margin-bottom: 3rem;
      padding-bottom: 2.5rem;
      border-bottom: 0.5px solid var(--border);
    }}
    .featured-post h2 {{
      font-family: var(--font-head);
      font-size: 1.55rem;
      font-weight: 700;
      line-height: 1.25;
      margin-bottom: 0.5rem;
    }}
    .featured-post h2 a {{ color: var(--text); text-decoration: none; }}
    .featured-post h2 a:hover {{ color: var(--accent); }}
    .post-meta {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      margin-bottom: 0.55rem;
      display: flex;
      gap: 1rem;
    }}
    .post-meta .category {{ color: var(--accent); }}
    .description {{
      font-size: 0.92rem;
      color: var(--muted);
      font-style: italic;
      line-height: 1.6;
      margin-bottom: 0.75rem;
    }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.6rem; }}
    .tag {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      padding: 0.15rem 0.55rem;
      border: 1px solid var(--border);
      border-radius: 2px;
      color: var(--muted);
    }}
    .about-block {{
      margin-bottom: 3rem;
      padding-bottom: 2.5rem;
      border-bottom: 0.5px solid var(--border);
      display: flex;
      gap: 1.5rem;
      align-items: flex-start;
    }}
    .about-block img {{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      object-fit: cover;
      flex-shrink: 0;
      filter: grayscale(15%);
    }}
    .about-text p {{
      font-size: 0.9rem;
      color: var(--muted);
      line-height: 1.7;
    }}
    .recent-posts {{ margin-bottom: 3rem; }}
    .post-list {{ list-style: none; }}
    .post-list li {{
      display: flex;
      gap: 1.25rem;
      align-items: baseline;
      padding: 0.65rem 0;
      border-bottom: 0.5px solid var(--border);
    }}
    .post-list li:first-child {{ border-top: 0.5px solid var(--border); }}
    .item-date {{
      font-family: var(--font-mono);
      font-size: 0.7rem;
      color: var(--muted);
      white-space: nowrap;
      min-width: 7.5ch;
    }}
    .post-list a {{
      font-size: 0.95rem;
      color: var(--text);
      text-decoration: none;
      line-height: 1.4;
    }}
    .post-list a:hover {{ color: var(--accent); }}
    .see-all {{
      display: inline-block;
      margin-top: 1rem;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--accent);
      text-decoration: none;
    }}
    .see-all:hover {{ text-decoration: underline; }}
    .books-block {{ margin-bottom: 3rem; }}
    .book-list {{ display: flex; flex-direction: column; }}
    .book-card {{
      padding: 1.1rem 0;
      border-bottom: 0.5px solid var(--border);
    }}
    .book-card:first-child {{ border-top: 0.5px solid var(--border); }}
    .book-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      margin-bottom: 0.35rem;
    }}
    .book-card h3 {{
      font-family: var(--font-body);
      font-size: 0.97rem;
      font-weight: 500;
      line-height: 1.3;
    }}
    .book-card h3 a {{ color: var(--text); text-decoration: none; }}
    .book-card h3 a:hover {{ color: var(--accent); }}
    .book-author {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      margin-top: 0.15rem;
    }}
    .book-year {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--rule);
      white-space: nowrap;
    }}
    .book-desc {{
      font-size: 0.85rem;
      color: var(--muted);
      font-style: italic;
      line-height: 1.6;
    }}
    .generated-note {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--rule);
      text-align: right;
      margin-bottom: 1rem;
    }}
    @media (max-width: 640px) {{
      .hero h1 {{ font-size: 2rem; }}
      .video-info {{ flex-direction: column; gap: 0.25rem; }}
      .about-block {{ flex-direction: column; }}
    }}
  </style>
</head>
<body>

  <nav class="topbar">
    <a class="btn" href="blog/">Blog →</a>
  </nav>

  <header class="hero">
    <p class="roles">Ingeniero de Sistemas · Divulgador tecnológico</p>
    <h1>César E. Uribe</h1>
    <p class="tagline">Desarrollo de sistemas para PYMEs y divulgación de inteligencia artificial aplicada.</p>
    <nav class="hero-links">
      <a href="mailto:cesaruribeperu@gmail.com">cesaruribeperu@gmail.com</a>
      <a href="https://www.youtube.com/@uribecesare" target="_blank" rel="noopener">YouTube</a>
    </nav>
  </header>
{video_html}
{featured_html}

  <section class="about-block">
    <img src="/image/pfp.png" alt="César Uribe">
    <div class="about-text">
      <p class="section-label">Acerca de</p>
      <p>Ingeniero de Sistemas con experiencia en desarrollo de soluciones para PYMEs. Divulgador tecnológico en Udemy y YouTube con enfoque en automatización mediante IA aplicada. Docente en Zegel IPAE y escritor aficionado.</p>
    </div>
  </section>
{recent_html}
{books_html}

  <p class="generated-note">Generado automáticamente · {now}</p>

{SHARED_FOOTER}

</body>
</html>"""


def render_blog_index(posts: list[dict]) -> str:
    def card(post):
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in post["tags"])
        return f"""
    <article class="post-card">
      <div class="post-meta">
        <time datetime="{post['date'].strftime('%Y-%m-%d')}">{post['date_str']}</time>
        {f'<span class="category">{post["category"]}</span>' if post["category"] else ""}
      </div>
      <h2><a href="{post['filename']}">{post['title']}</a></h2>
      {f'<p class="description">{post["description"]}</p>' if post["description"] else ""}
      {f'<div class="tags">{tags_html}</div>' if tags_html else ""}
    </article>"""

    cards = "\n".join(card(p) for p in posts)
    count = len(posts)
    now   = datetime.now().strftime("%d %b %Y, %H:%M")

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Blog — César Uribe</title>
  <meta name="description" content="Artículos sobre inteligencia artificial aplicada, prompt engineering y tecnología.">
  {FAVICON}
  {SHARED_FONTS}
  <style>{SHARED_CSS}
    nav.breadcrumb {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      letter-spacing: 0.06em;
      color: var(--muted);
      margin: 2rem 0 2.5rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    nav.breadcrumb a {{ color: var(--accent); text-decoration: none; }}
    nav.breadcrumb a:hover {{ text-decoration: underline; }}
    nav.breadcrumb .sep {{ color: var(--rule); }}
    .page-header {{
      border-bottom: 1.5px solid var(--accent);
      padding-bottom: 1.5rem;
      margin-bottom: 3rem;
    }}
    .page-header h1 {{
      font-family: var(--font-head);
      font-size: 2.4rem;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 0.5rem;
    }}
    .page-header .count {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--muted);
    }}
    .post-list-full {{ display: flex; flex-direction: column; }}
    .post-card {{ padding: 1.75rem 0; border-bottom: 0.5px solid var(--border); }}
    .post-card:first-child {{ border-top: 0.5px solid var(--border); }}
    .post-meta {{
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--muted);
      margin-bottom: 0.6rem;
      display: flex;
      gap: 1rem;
    }}
    .post-meta .category {{ color: var(--accent); }}
    .post-card h2 {{
      font-family: var(--font-head);
      font-size: 1.35rem;
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: 0.55rem;
    }}
    .post-card h2 a {{ color: var(--text); text-decoration: none; }}
    .post-card h2 a:hover {{ color: var(--accent); }}
    .description {{
      font-size: 0.92rem;
      color: var(--muted);
      font-style: italic;
      line-height: 1.6;
      margin-bottom: 0.75rem;
    }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.6rem; }}
    .tag {{
      font-family: var(--font-mono);
      font-size: 0.68rem;
      padding: 0.15rem 0.55rem;
      border: 1px solid var(--border);
      border-radius: 2px;
      color: var(--muted);
    }}
    .generated-note {{
      margin-top: 3rem;
      font-family: var(--font-mono);
      font-size: 0.68rem;
      color: var(--rule);
      text-align: right;
    }}
    @media (max-width: 640px) {{ .page-header h1 {{ font-size: 1.85rem; }} }}
  </style>
</head>
<body>

  <nav class="breadcrumb">
    <a href="https://uribecesar.github.io">Inicio</a>
    <span class="sep">/</span>
    <span>Blog</span>
  </nav>

  <header class="page-header">
    <h1>Blog</h1>
    <p class="count">{count} {"artículo" if count == 1 else "artículos"} publicados</p>
  </header>

  <section class="post-list-full">
{cards}
  </section>

  <p class="generated-note">Generado automáticamente · {now}</p>

{SHARED_FOOTER}

</body>
</html>"""


def main():
    posts   = collect_posts()
    content = load_content()

    home_path = ROOT / "index.html"
    home_path.write_text(render_home(posts, content), encoding="utf-8")
    print(f"Landing generado    → {home_path}")

    blog_path = ROOT / "blog" / "index.html"
    if blog_path.parent.exists():
        blog_path.write_text(render_blog_index(posts), encoding="utf-8")
        print(f"Blog index generado → {blog_path}  ({len(posts)} artículos)")
    else:
        print("Carpeta blog/ no encontrada, índice de blog omitido.")

    videos = content.get("videos", [])
    libros = content.get("libros", [])
    print(f"Contenido cargado   → {len(videos)} video(s), {len(libros)} libro(s)")

    skipped = []
    blog_dir = ROOT / "blog"
    if blog_dir.exists():
        for path in blog_dir.glob("*.html"):
            if path.name == "index.html":
                continue
            p = MetaExtractor()
            p.feed(path.read_text(encoding="utf-8"))
            if p.meta.get("post:status", "").strip().lower() != "published":
                skipped.append(path.name)

    if skipped:
        print(f"Omitidos (draft):   {', '.join(skipped)}")


if __name__ == "__main__":
    main()
