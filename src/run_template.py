"""
Run a template notebook with papermill, but only up to the cell tagged
``stop-execution``. Remaining cells are appended unexecuted so the user can
run them manually in JupyterLab.

This exists because papermill executes the whole notebook in a single
process at container start. For datasets with large parquet files that
exceeds the memory available on renkulab.io and the kernel is killed
before JupyterLab is even up. Splitting the notebook lets us still render
metadata at startup without loading the data eagerly.
"""

import sys
from pathlib import Path

import nbformat
import papermill as pm

STOP_TAG = "stop-execution"


def main(template_path: str, output_path: str, package_id: str, resource_id: str) -> None:
    template = Path(template_path)
    output = Path(output_path)

    nb = nbformat.read(template, as_version=4)

    stop_idx = next(
        (i for i, c in enumerate(nb.cells) if STOP_TAG in c.metadata.get("tags", [])),
        len(nb.cells),
    )

    head = nbformat.v4.new_notebook()
    head.metadata = nb.metadata
    head.cells = nb.cells[:stop_idx]
    tail_cells = nb.cells[stop_idx:]

    head_path = output.with_name(f"_{output.stem}_head.ipynb")
    nbformat.write(head, head_path)

    try:
        pm.execute_notebook(
            str(head_path),
            str(output),
            parameters={"package_id": package_id, "resource_id": resource_id},
        )
    finally:
        head_path.unlink(missing_ok=True)

    executed = nbformat.read(output, as_version=4)
    executed.cells.extend(tail_cells)
    nbformat.write(executed, output)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print(
            "Usage: run_template.py <template> <output> <package_id> <resource_id>",
            file=sys.stderr,
        )
        sys.exit(1)
    main(*sys.argv[1:5])
