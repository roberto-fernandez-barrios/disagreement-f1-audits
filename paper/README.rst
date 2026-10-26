Author manuscript
=================

`paper.pdf <paper.pdf>`_ is the canonical six-page **V4** author manuscript,
prepared for the ESANN 2027 general track. It is not yet submitted or accepted.
Repository releases 1.2.0 and 1.3.0 preserve its exact bytes.

* ``source/`` contains the LaTeX source, official ESANN class, tables and figure.
* ``references/`` contains source attribution records and the original template.

From the repository root, ``python tools/manage.py build`` compiles a separate
PDF using an existing MiKTeX or TeX Live installation and checks its layout.
See the `build instructions <../docs/reproduction.rst>`_. The delivered PDF is
never overwritten. Historical build records are in
``reproducibility/records/pdf_build/``.

The manuscript's reserved Zenodo DOI is still pending publication. Current
public access is through the versioned GitHub release; see the repository
README for availability and editorial status. Manuscript license: CC BY 4.0.
