Contributing and reporting issues
=================================

For a question or reproducible defect, open an issue in this repository. Include
the release tag/commit, OS, Python version, command and relevant log excerpt.
Use a small synthetic example when possible; do not post private labels,
credentials or restricted source data. Numerical objections should identify
the feasible completions or the exact claim that appears inconsistent.

For interface changes, run::

    python -m unittest discover -s tests -v
    python tools/manage.py manifest
    python tools/manage.py verify

The manifest command is a deliberate maintainer operation. It refreshes the
current package hashes but rejects any change to the frozen scientific snapshot.
Do not use it to conceal an unexpected mismatch. A scientific revision needs
a new identified snapshot, appropriate analysis/review and a new release while
retaining the previous files and interpretation.

Commands run in isolated ``.work/`` copies. Do not edit historical execution
records or rewrite the original protocol. The public entry point is
``tools/manage.py``; root scripts are preserved for scientific provenance.

Release procedure
-----------------

1. Update the release metadata, citation, documentation and changelog honestly.
2. Refresh the manifest and verify the frozen scientific files.
3. Test the interface and affected reconstruction/build paths in a clean
   environment; wait for the applicable CI jobs to pass.
4. Run ``tools/manage.py package`` and verify a fresh extraction. Confirm the
   canonical PDF matches the file in the ZIP.
5. Create a new tag/release and publish the ZIP, PDF, checksums and validation
   record. Download the public files and compare their hashes.
6. Publish/update archival identifiers only when authorized and accessible.
   A reserved DOI must be labeled pending until its public record resolves.

Repository quality and model-review agreement do not establish scientific
novelty or editorial acceptance. State the actual submission/publication status.
