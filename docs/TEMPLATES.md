# Template guide / 模板说明

A template describes one recurring layout. The UI can export/import its JSON. The default `templates/quotation.json` supports only the supplied quotation samples.

## Configuration

- `name`: a human-readable label.
- `page_size`: optional `[width, height]` in PDF points (72 points per inch); accepts a 2-point tolerance. Letter is `[612, 792]`; A4 is approximately `[595.28, 841.89]`. Omit the field if page size need not be constrained.
- `bbox`: `[left, top, right, bottom]` as fractions of page width/height, between 0 and 1. `[0, 0, 1, 1]` means the whole page. Choose a region containing the complete table and no other tables. Coordinates start at the top-left.
- `columns`: ordered names matching the first row of the PDF table. Whitespace is collapsed and comparison is case-insensitive. `type` is `text` or `number`. `required` defaults to `true`; set `false` only when a blank is valid for that field.
- `checks`: optional multiplication checks referencing numeric columns. For example, `{"left":"Qty","right":"Unit price","equals":"Amount"}` flags discrepancies above 0.01. It never corrects the source amount. This tolerance is fixed in v0.1.

Use `text` for product codes, account numbers and identifiers. A code like `001` must not be declared `number`.

Each page must repeat the same single header row. No totals/footer rows may be present inside the detected table unless they match every configured column requirement and are intentionally to be included. There is no automatic detection or removal of subtotal rows.

## Adapting a client document

1. Obtain an authorized, preferably redacted sample.
2. Confirm that text is selectable and there is a visible ruled table.
3. Set page size, table region and ordered header names.
4. Mark numeric columns explicitly; keep identifiers as text.
5. Convert a short sample and compare every cell against the PDF.
6. Test a second page and a second file of the same layout.
7. Save the template with a generic name; do not commit client-specific data.

Use a separate template for a different layout. Passing the header checks alone does not prove that every cell was extracted correctly. Missing text inside a merged cell, unusual fonts, clipped columns and row segmentation can require manual work or a different extraction strategy.
