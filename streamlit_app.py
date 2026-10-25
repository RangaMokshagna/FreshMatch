"""Compatibility wrapper for Streamlit Cloud deployments.

This project keeps the full app in `app.py`, but streamlit hosting checks for a
common entry-point file such as `streamlit_app.py`. Re-executing the canonical
script here keeps the app behavior identical while satisfying the deployment
file-path requirement.
"""

from __future__ import annotations

if __name__ == "__main__":
    import runpy

    runpy.run_path("app.py", run_name="__main__")
else:
    import app  # noqa: F401
