# Fixes from the pre-push review

These follow-up portfolio improvements address the two findings reported after Step 2. They preserve existing saved records and team credits.

## Saved habit and workout text interpreted as HTML

**Symptom and reproduction:** A habit name/category/unit or workout type/notes containing HTML was interpolated into a card's `innerHTML`. When the saved record displayed, the browser could create elements and run event handlers embedded in that text. Both the habit inventory and daily checklist had this issue.

**Root cause:** User-provided strings shared the same template interpolation path as trusted layout markup.

**Fix:** `frontend/js/record-renderers.js` now owns habit inventory cards, checklist rows, and workout cards. Their static layouts contain no interpolated saved fields. Each field is assigned with `textContent`. Checkbox, increment, and delete behavior uses event listeners with callbacks rather than inline handlers. The home screen calls these builders, preserving its existing visual classes and controller logic. Existing database content needs no migration or deletion.

**Verification:** A real headless Chrome loads the actual rendering module from a self-contained temporary page. The fixture supplies image/SVG event-handler payloads and checks that names, categories, units, types, and notes remain literal text; no injected elements or handlers appear. It also checks checkbox state/events, increment sizes, deletion callbacks, core-habit protection, duration formatting, and the missing-notes fallback.

## Interactive API documentation omitted a required header

**Symptom and reproduction:** `/docs` offered POST/PUT/DELETE operations without an input for `X-PulsePoint-Request`. Requests generated there failed with HTTP 403 even with otherwise valid input.

**Root cause:** Middleware enforced the header, but OpenAPI did not describe it.

**Fix:** `dependencies/request_protection.py` keeps the header name/value shared with middleware and adds a required header parameter, with default/allowed value `1`, to mutating OpenAPI operations. Swagger UI exposes this prefilled value. Existing schema parameters are retained, repeated schema requests do not duplicate it, and read-only operations do not require it. Server validation and cross-origin restrictions remain in effect.

**Verification:** API regressions inspect every operation in the generated schema, then use exactly the advertised header to sign up, log in, create/update/delete a workout, and log out against the isolated test database. A missing header still returns HTTP 403.

## Organization and test results

- Added the rendering module under the existing `frontend/js/` folder, and removed its duplicated templates and now-unused duration helper from `home.js`.
- Added the browser fixture under `tests/frontend/` and its Python runner alongside the existing authentication suite.
- Kept request-protection metadata in a focused dependency module rather than expanding route files or rearranging the repository.
- The full suite passed: **19 tests**, including the Chrome rendering check. API tests used only temporary SQLite; rendering checks used no database. The first sandboxed run could not launch Chrome; the rerun with local browser execution permission passed.
- Existing Starlette test-client and workout timestamp deprecation warnings remain unrelated to these fixes.

Run from the repository root:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

No real user records, credentials, browser profiles, paid services, or database exports are part of the added tests. The application's Uvicorn server is not needed for this suite.
