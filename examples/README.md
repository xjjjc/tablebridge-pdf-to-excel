# Synthetic examples

These files contain fictional data created for this project; they are not client documents.

- `demo-quotation.pdf`: two pages, eight rows, compatible with the bundled template.
- `demo-amount-warning.pdf`: two rows with one intentional amount discrepancy.
- `demo-wrong-layout.pdf`: an incompatible header that should be rejected.
- `demo-output.xlsx`: the normal quotation converted to Data, Raw text and Review sheets.

Use `python scripts/create_samples.py` to regenerate the PDF fixtures. Run the local app to convert them and compare results.
