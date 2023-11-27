# conf.py

import os
import sys

# -- Project information -----------------------------------------------------

project = 'journal entry maker'
author = 'mohamed elnabarawi'

# -- General configuration ---------------------------------------------------

# Add extensions (optional)
extensions = [
    'sphinx.ext.autodoc',  # Automatically document code
    'sphinx.ext.napoleon',  # Support for Google-style docstrings
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix(es) of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory.
html_static_path = ['_static']

# -- Options for HTMLHelp output ---------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'journalentrymaker'

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
}

# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'yourproject', 'Your Project Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'YourProject', 'Your Project Documentation',
     author, 'YourProject', 'One line description of project.',
     'Miscellaneous'),
]

# -- Autodoc settings --------------------------------------------------------

# Enable automatic docstring extraction
# Add any dependencies to mock if needed
autodoc_mock_imports = ["your_dependency"]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute.
sys.path.insert(0, os.path.abspath('.'))

# -- Additional settings -----------------------------------------------------
