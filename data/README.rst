Frozen inputs
=============

These are derived predictions and labels, not the original feature datasets.
All scientific input files retain the exact bytes used for manuscript V4.

* ``predictions/v9/`` and ``predictions/v10/`` hold the 90 frozen TDC files.
  The version labels identify the source TDC export families, not new studies.
* ``validation/`` holds validation scores, selection information and its
  original manifest. The associated exporters are under
  ``reproducibility/source_exports/``.
* ``controls/`` holds the saved weak-zero stops and earlier diagnostic used
  to check the zero-loss control independently.

The source is TDC prediction artifact **1.1.6**,
`10.5281/zenodo.21776862 <https://doi.org/10.5281/zenodo.21776862>`_.
For source details and limitations, see `provenance <../docs/provenance.rst>`_.
The original manifests use historical paths. The
`path map <../reproducibility/frozen_files.json>`_ identifies each current file
and its original SHA-256; the public verification command checks them all.

Full target labels support retrospective verification. The public audit adapter
uses only the observations supplied by its caller. The original query policies
and stopping rules retain their information restrictions.
