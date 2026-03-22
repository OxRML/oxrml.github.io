# oxrml.github.io
GitHub Page for the Reasoning with Machines Lab website: https://oxrml.com/


## Contributing

We push directly to main. Please test changes locally before committing (you might need to create an environment first with python installed):

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://localhost:8000` in your browser to verify the changes.

## Adding Research, News or Team Members

Content is managed through JSON:

- Research entries live in `research.json` under `publications`
- News entries live in `news.json`

Research example:

```json
{
  "id": "example_paper",
  "date": "2026-03-22",
  "displayDate": "March 2026",
  "title": "Example Research Title",
  "authors": "A Author, B Author",
  "labMembers": ["A Author"],
  "pubDate": "2026",
  "venue": "Conference or Journal",
  "home_display": true,
  "abstract": "Short abstract",
  "webp_path": "img/publications/example.webp",
  "links": {
    "preprint_link": "https://arxiv.org/abs/...",
    "paper_link": "https://...",
    "github_link": "https://github.com/...",
    "website_link": "https://...",
    "hf_link": "https://huggingface.co/...",
    "youtube_link": "https://youtube.com/..."
  }
}
```

Fields:

- `id`: unique slug
- `date`: machine-sortable date in `YYYY-MM-DD`
- `displayDate` / `pubDate`: what appears on the site
- `title`, `authors`, `venue`, `abstract`: display content
- `labMembers`: lab authors used for filtering
- `home_display`: whether it appears on the homepage
- `webp_path`: card image
- `links`: optional external links

News example:

```json
{
  "id": "example_news",
  "date": "2026-03-22",
  "displayDate": "March 2026",
  "title": "Example News Title",
  "text": "Short update text.",
  "category": "paper",
  "photos": [
    {
      "src": "img/news/example.png",
      "alt": "Example image",
      "fit": "contain"
    }
  ],
  "span_links": {
    "Short update text": "https://example.com"
  }
}
```

Fields:

- `id`, `date`, `displayDate`, `title`: basic metadata
- `text`: main update text
- `category`: e.g. `paper`, `conference`, `award`, `media`, `milestone`
- `photos`: optional images with `src`, `alt`, and `fit`; if there is more than one, the site shows them as a slideshow
- `span_links`: optional text-to-link mapping inside the update
- `bullets`: optional list of bullet points, useful when grouping multiple papers in one update

### Recent Work Policy

- When a paper first appears on arXiv, add a `New Preprints` news item
- If multiple papers appear around the same time, group them into one news item and list them in `bullets`
- Once the papers are accepted or rejected, remove the preprint news item and replace it with acceptance news
- Once the team presents the work at the conference, remove the acceptance news and replace it with `OxRML @ <Conference>`
