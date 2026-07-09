from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from config import APP_NAME, HOST, PORT


MOVIES = [
    {
        "id": 1,
        "title": "Midnight Signal",
        "year": 2026,
        "rating": "TV-14",
        "genre": "Sci-Fi",
        "duration": "1h 54m",
        "match": 98,
        "description": "A radio engineer catches a future broadcast and races to stop a citywide blackout.",
        "color": "#c1121f",
    },
    {
        "id": 2,
        "title": "The Last Monsoon",
        "year": 2025,
        "rating": "PG-13",
        "genre": "Drama",
        "duration": "2h 08m",
        "match": 95,
        "description": "Three strangers meet on a delayed train as the rain changes the course of their lives.",
        "color": "#0f766e",
    },
    {
        "id": 3,
        "title": "Code Red City",
        "year": 2026,
        "rating": "TV-MA",
        "genre": "Action",
        "duration": "1h 47m",
        "match": 93,
        "description": "A retired driver returns for one impossible night job through a locked-down metropolis.",
        "color": "#991b1b",
    },
    {
        "id": 4,
        "title": "Cafe Comet",
        "year": 2024,
        "rating": "U/A",
        "genre": "Comedy",
        "duration": "1h 31m",
        "match": 90,
        "description": "A tiny coffee shop becomes the meeting point for people with wonderfully bad timing.",
        "color": "#b45309",
    },
    {
        "id": 5,
        "title": "North Door",
        "year": 2025,
        "rating": "TV-14",
        "genre": "Thriller",
        "duration": "1h 59m",
        "match": 96,
        "description": "A journalist finds one door in an old hotel that appears in a different place every night.",
        "color": "#334155",
    },
    {
        "id": 6,
        "title": "Pixel Hearts",
        "year": 2026,
        "rating": "PG",
        "genre": "Romance",
        "duration": "1h 42m",
        "match": 91,
        "description": "Two indie game developers fall in love while building a project that keeps breaking.",
        "color": "#be185d",
    },
    {
        "id": 7,
        "title": "Deep Orbit",
        "year": 2023,
        "rating": "TV-PG",
        "genre": "Sci-Fi",
        "duration": "2h 16m",
        "match": 89,
        "description": "A rescue crew reaches a silent research station and discovers it was never abandoned.",
        "color": "#1d4ed8",
    },
    {
        "id": 8,
        "title": "Street Food Kings",
        "year": 2026,
        "rating": "TV-G",
        "genre": "Documentary",
        "duration": "48m",
        "match": 94,
        "description": "Vendors across India share the craft, pressure, and pride behind their signature dishes.",
        "color": "#15803d",
    },
]


def movie_rows():
    featured = sorted(MOVIES, key=lambda movie: movie["match"], reverse=True)
    return {
        "Trending Now": featured[:5],
        "New Releases": sorted(MOVIES, key=lambda movie: movie["year"], reverse=True)[:5],
        "Because You Like Thrillers": [movie for movie in MOVIES if movie["genre"] in {"Thriller", "Action", "Sci-Fi"}],
        "Feel Good Picks": [movie for movie in MOVIES if movie["genre"] in {"Comedy", "Romance", "Documentary"}],
    }


def render_page():
    hero = MOVIES[0]
    genres = sorted({movie["genre"] for movie in MOVIES})
    rows = movie_rows()
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{APP_NAME}</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #070707;
      --panel: #141414;
      --muted: #a3a3a3;
      --text: #f5f5f5;
      --red: #e50914;
      --line: rgba(255, 255, 255, .12);
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      min-height: 100vh;
      background: var(--bg);
      color: var(--text);
      font-family: Arial, Helvetica, sans-serif;
    }}

    header {{
      position: fixed;
      inset: 0 0 auto;
      z-index: 10;
      display: flex;
      align-items: center;
      gap: 24px;
      padding: 18px clamp(18px, 4vw, 56px);
      background: linear-gradient(180deg, rgba(0,0,0,.86), rgba(0,0,0,.08));
    }}

    .brand {{
      color: var(--red);
      font-size: clamp(1.6rem, 4vw, 2.4rem);
      font-weight: 900;
      letter-spacing: 0;
      text-transform: uppercase;
    }}

    nav {{
      display: flex;
      gap: 18px;
      color: #ddd;
      font-size: .95rem;
    }}

    .tools {{
      margin-left: auto;
      display: flex;
      gap: 10px;
      align-items: center;
    }}

    input, select {{
      height: 38px;
      border: 1px solid var(--line);
      border-radius: 4px;
      background: rgba(0, 0, 0, .58);
      color: var(--text);
      padding: 0 12px;
      outline: none;
    }}

    input {{ width: min(260px, 32vw); }}

    .hero {{
      min-height: 78vh;
      display: grid;
      align-items: end;
      padding: 120px clamp(18px, 4vw, 56px) 72px;
      background:
        linear-gradient(90deg, rgba(0,0,0,.88), rgba(0,0,0,.38), rgba(0,0,0,.8)),
        linear-gradient(135deg, {hero["color"]}, #050505 58%);
    }}

    .hero-content {{ max-width: 640px; }}

    h1 {{
      margin: 0 0 14px;
      font-size: clamp(3rem, 8vw, 6rem);
      line-height: .95;
      letter-spacing: 0;
    }}

    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      align-items: center;
      color: #e5e5e5;
      font-weight: 700;
      margin-bottom: 14px;
    }}

    .match {{ color: #22c55e; }}

    .hero p {{
      max-width: 56ch;
      color: #e7e7e7;
      font-size: 1.12rem;
      line-height: 1.5;
    }}

    .actions {{ display: flex; gap: 12px; margin-top: 24px; }}

    button {{
      border: 0;
      border-radius: 4px;
      min-height: 42px;
      padding: 0 18px;
      font-size: 1rem;
      font-weight: 800;
      cursor: pointer;
    }}

    .play {{ background: #fff; color: #111; }}
    .secondary {{ background: rgba(109,109,110,.72); color: #fff; }}

    main {{ padding: 0 clamp(18px, 4vw, 56px) 48px; }}

    .row {{ margin-top: 28px; }}

    h2 {{
      margin: 0 0 12px;
      font-size: 1.25rem;
    }}

    .rail {{
      display: grid;
      grid-auto-flow: column;
      grid-auto-columns: minmax(210px, 1fr);
      gap: 12px;
      overflow-x: auto;
      padding-bottom: 12px;
      scrollbar-color: #555 transparent;
    }}

    .card {{
      min-height: 162px;
      border-radius: 6px;
      background: var(--panel);
      border: 1px solid var(--line);
      overflow: hidden;
      cursor: pointer;
      transition: transform .18s ease, border-color .18s ease;
    }}

    .card:hover {{
      transform: translateY(-4px);
      border-color: rgba(255,255,255,.36);
    }}

    .poster {{
      height: 98px;
      display: grid;
      place-items: center;
      padding: 12px;
      background: linear-gradient(135deg, var(--movie-color), #111 70%);
      font-size: 1.05rem;
      font-weight: 900;
      text-align: center;
    }}

    .card-body {{ padding: 10px 12px 12px; }}
    .card-title {{ font-weight: 800; margin-bottom: 6px; }}
    .card .meta {{ font-size: .78rem; color: var(--muted); margin: 0; gap: 8px; }}

    dialog {{
      width: min(680px, calc(100vw - 28px));
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #101010;
      color: var(--text);
      padding: 0;
    }}

    dialog::backdrop {{ background: rgba(0,0,0,.76); }}

    .modal-art {{
      min-height: 210px;
      background: linear-gradient(135deg, var(--movie-color), #111 70%);
      padding: 24px;
      display: flex;
      align-items: end;
    }}

    .modal-body {{ padding: 22px 24px 24px; }}
    .modal-body h3 {{ margin: 0 0 10px; font-size: 2rem; }}
    .modal-body p {{ color: #ddd; line-height: 1.55; }}

    .empty {{
      display: none;
      color: var(--muted);
      margin: 34px 0;
    }}

    @media (max-width: 720px) {{
      header {{ align-items: flex-start; flex-direction: column; gap: 12px; }}
      nav {{ display: none; }}
      .tools {{ width: 100%; margin-left: 0; }}
      input {{ flex: 1; width: auto; }}
      select {{ width: 124px; }}
      .hero {{ min-height: 72vh; padding-top: 152px; }}
      .rail {{ grid-auto-columns: minmax(170px, 72vw); }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="brand">{APP_NAME}</div>
    <nav>
      <span>Home</span>
      <span>Series</span>
      <span>Movies</span>
      <span>My List</span>
    </nav>
    <div class="tools">
      <input id="search" type="search" placeholder="Search titles">
      <select id="genre">
        <option value="">All genres</option>
        {"".join(f'<option value="{genre}">{genre}</option>' for genre in genres)}
      </select>
    </div>
  </header>

  <section class="hero">
    <div class="hero-content">
      <h1>{hero["title"]}</h1>
      <div class="meta">
        <span class="match">{hero["match"]}% Match</span>
        <span>{hero["year"]}</span>
        <span>{hero["rating"]}</span>
        <span>{hero["duration"]}</span>
      </div>
      <p>{hero["description"]}</p>
      <div class="actions">
        <button class="play" data-open="{hero["id"]}">Play</button>
        <button class="secondary" data-list="{hero["id"]}">+ My List</button>
      </div>
    </div>
  </section>

  <main id="catalog">
    {"".join(render_row(title, movies) for title, movies in rows.items())}
    <p class="empty" id="empty">No titles match your search.</p>
  </main>

  <dialog id="details">
    <div class="modal-art">
      <h3 id="modal-title"></h3>
    </div>
    <div class="modal-body">
      <div class="meta" id="modal-meta"></div>
      <p id="modal-description"></p>
      <div class="actions">
        <button class="play">Play</button>
        <button class="secondary" id="modal-list">+ My List</button>
        <button class="secondary" id="close">Close</button>
      </div>
    </div>
  </dialog>

  <script>
    const movies = {json.dumps(MOVIES)};
    const search = document.querySelector("#search");
    const genre = document.querySelector("#genre");
    const empty = document.querySelector("#empty");
    const dialog = document.querySelector("#details");
    const watchlist = new Set(JSON.parse(localStorage.getItem("watchlist") || "[]"));

    function persistList() {{
      localStorage.setItem("watchlist", JSON.stringify([...watchlist]));
    }}

    function openMovie(id) {{
      const movie = movies.find(item => item.id === Number(id));
      if (!movie) return;
      dialog.style.setProperty("--movie-color", movie.color);
      document.querySelector("#modal-title").textContent = movie.title;
      document.querySelector("#modal-meta").innerHTML = `<span class="match">${{movie.match}}% Match</span><span>${{movie.year}}</span><span>${{movie.rating}}</span><span>${{movie.genre}}</span><span>${{movie.duration}}</span>`;
      document.querySelector("#modal-description").textContent = movie.description;
      document.querySelector("#modal-list").dataset.list = movie.id;
      dialog.showModal();
    }}

    function toggleList(id) {{
      const movieId = Number(id);
      if (watchlist.has(movieId)) {{
        watchlist.delete(movieId);
      }} else {{
        watchlist.add(movieId);
      }}
      persistList();
      renderListButtons();
    }}

    function renderListButtons() {{
      document.querySelectorAll("[data-list]").forEach(button => {{
        button.textContent = watchlist.has(Number(button.dataset.list)) ? "✓ My List" : "+ My List";
      }});
    }}

    function filterCards() {{
      const term = search.value.trim().toLowerCase();
      const pickedGenre = genre.value;
      let visibleCount = 0;

      document.querySelectorAll(".card").forEach(card => {{
        const title = card.dataset.title.toLowerCase();
        const cardGenre = card.dataset.genre;
        const visible = title.includes(term) && (!pickedGenre || cardGenre === pickedGenre);
        card.hidden = !visible;
        if (visible) visibleCount += 1;
      }});

      document.querySelectorAll(".row").forEach(row => {{
        row.hidden = !row.querySelector(".card:not([hidden])");
      }});

      empty.style.display = visibleCount ? "none" : "block";
    }}

    document.addEventListener("click", event => {{
      const opener = event.target.closest("[data-open]");
      const listButton = event.target.closest("[data-list]");
      if (opener) openMovie(opener.dataset.open);
      if (listButton) toggleList(listButton.dataset.list);
    }});

    document.querySelector("#close").addEventListener("click", () => dialog.close());
    search.addEventListener("input", filterCards);
    genre.addEventListener("change", filterCards);
    renderListButtons();
  </script>
</body>
</html>"""


def render_row(title, movies):
    cards = "".join(render_card(movie) for movie in movies)
    return f"""<section class="row">
      <h2>{title}</h2>
      <div class="rail">{cards}</div>
    </section>"""


def render_card(movie):
    style = f' style="--movie-color: {movie["color"]}"'
    return f"""<article class="card" data-open="{movie["id"]}" data-title="{movie["title"]}" data-genre="{movie["genre"]}"{style}>
      <div class="poster">{movie["title"]}</div>
      <div class="card-body">
        <div class="card-title">{movie["title"]}</div>
        <div class="meta">
          <span class="match">{movie["match"]}%</span>
          <span>{movie["year"]}</span>
          <span>{movie["genre"]}</span>
        </div>
      </div>
    </article>"""


class NitflixHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.respond(render_page(), "text/html; charset=utf-8")
            return
        if path == "/api/movies":
            self.respond(json.dumps(MOVIES), "application/json")
            return
        self.send_error(404, "Page not found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/search":
            self.send_error(404, "Page not found")
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = self.rfile.read(length).decode("utf-8")
        query = parse_qs(payload).get("q", [""])[0].lower()
        results = [movie for movie in MOVIES if query in movie["title"].lower()]
        self.respond(json.dumps(results), "application/json")

    def respond(self, body, content_type):
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        print(f"{self.address_string()} - {format % args}")


def main():
    server = ThreadingHTTPServer((HOST, PORT), NitflixHandler)
    print(f"{APP_NAME} is running at http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
