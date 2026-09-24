# Verification report

Development verification date: 2026-09-24. Synthetic documents only; no customer data or performance claims.

## Automated checks

`python -m unittest discover -s tests -v`

Nine tests passed in the development environment:

1. Two-page extraction returns eight expected identifiers, numeric values and page references.
2. A deliberately wrong source amount produces a warning and remains unchanged.
3. A different header layout is rejected.
4. A blank page without selectable text is rejected.
5. Invalid non-PDF input is rejected.
6. Invalid column, region and page-size templates are rejected.
7. Excel round-trip preserves identifier text, numeric cells and raw multiline text.
8. Formula-like source text remains literal, with no generated formula cells.
9. A two-file export preserves both file references and all ten data rows.

## HTTP and interface checks

The real local HTTP handler was exercised with static assets, a two-page conversion and a downloaded XLSX reopened for verification, a two-file batch with an arithmetic warning, rejection of an entire batch containing an incompatible PDF, an invalid request token, and duplicate filenames. These checks passed. JavaScript syntax was checked separately.

Interactive browser verification could not be completed: a local Chromium executable was unavailable, and the available remote browser could not access the localhost application. A visual screenshot and browser-click success are therefore not claimed. Run the example flow on a local computer before demonstrating the app to clients.

## Limits of this evidence

These fixtures demonstrate the intended layout only. They do not establish accuracy across arbitrary invoices, languages, fonts or scanned documents. Windows startup and the GitHub Actions matrix need execution on their target platforms. No load test, hostile-PDF security audit or public hosting test has been performed.
