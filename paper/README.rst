Author manuscript
=================

`paper.pdf <paper.pdf>`_ is the canonical six-page **V5** author manuscript,
prepared for the ESANN 2027 general track. It is not yet submitted or accepted.
Release 1.4.0 revises literature positioning and attribution without changing numerical results.
The V4 source/PDF remain under reproducibility/history/v4 and in prior releases.

* ``source/`` contains the LaTeX source, official ESANN class, tables and figure.
* ``references/`` contains source attribution records and the original template.

From the repository root, ``python tools/manage.py build`` compiles a separate
PDF using an existing MiKTeX or TeX Live installation and checks its layout.
See the `build instructions <../docs/reproduction.rst>`_. The delivered PDF is
never overwritten. Historical build records are in
``reproducibility/records/pdf_build/``.

Version-specific archive: https://doi.org/10.5281/zenodo.23647323.
This release reuses the previously empty reserved draft, preserving published
version 1.0.0. Manuscript license: CC BY 4.0.
