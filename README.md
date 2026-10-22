# oxrml.github.io
GitHub Page for the Reasoning with Machines Lab website: https://oxrml.com/


## Contributing

We push directly to main. Please test changes locally before committing (you might need to create an environment first with python installed):

```bash
python -m http.server 8000 --bind 127.0.0.1
```

Then visit `http://localhost:8000` in your browser to verify the changes.

## Notes

- Keep `.nojekyll`: without it GitHub Pages skips the `_astro/` folder and the site loses its styles.
- Pages from the previous site (`research.html`, `team.html`, `news.html`, `contact.html`, and the old top-level project pages such as `/faithfulness/`) are now small redirect pages pointing to their new locations, so existing links keep working.
