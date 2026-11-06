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

## HelpMed interactive display

`helpmed/index.html` serves the standalone HelpMed display at https://oxrml.com/helpmed/.
It is available directly by URL, without an entry in the main site's navigation.
The file includes its own styles, scripts, conversation data, fonts, and logos; no build or backend is needed on GitHub Pages.

Source: [mkussman26/helpmed-HoL-stand](https://github.com/mkussman26/helpmed-HoL-stand), commit `084509433372834a939f39d324d6e4609613478c`.
To update it, copy the upstream generated `index.html` to `helpmed/index.html`.
If editing upstream sources, run `python3 build/build.py` in that repository first.
Use the local server above to check `/helpmed` (which redirects to `/helpmed/`), conversation playback, and the quiz before publishing.

Publish `helpmed/index.html` through the normal GitHub Pages deployment from `main`.
The existing `CNAME` already points to `oxrml.com`; no DNS, navigation, or build configuration changes are needed.

Browser validation (Chromium, 6 November 2026): direct URL access, all four looping conversations,
all three quiz conversations (nine questions), correct/incorrect feedback, scoring, exit flows,
pause/resume, failure definitions, fullscreen, and offline interaction passed.
Desktop (1920×1080) and laptop (1366×768) layouts were checked, with no browser errors or failed asset requests.
