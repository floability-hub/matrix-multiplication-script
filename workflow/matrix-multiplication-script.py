#!/usr/bin/env python3
"""Multiply every unique pair of staged matrices with TaskVine."""

import itertools
import os
from pathlib import Path

import ndcctools.taskvine as vine


def multiply_matrices(path_a, path_b):
    """Load two matrices, multiply them, and return a small result."""

    from pathlib import Path

    import numpy as np

    matrix_a = np.loadtxt(path_a, delimiter=",")
    matrix_b = np.loadtxt(path_b, delimiter=",")
    product = matrix_a @ matrix_b

    return (
        Path(path_a).stem,
        Path(path_b).stem,
        product.shape,
        float(np.linalg.norm(product)),
    )


def main():
    matrix_files = sorted(Path("data/matrices").glob("matrix_dense_*.csv"))
    
    if len(matrix_files) < 2:
        raise RuntimeError("Floability did not stage enough matrix files")

    manager_name = os.environ["VINE_MANAGER_NAME"]
    ports_text = os.environ.get("VINE_MANAGER_PORTS", "9123,9150")
    
    manager_ports = [
        int(port) for port in ports_text.replace(":", ",").split(",")
    ]

    print(f"[manager] Starting {manager_name}")
    manager = vine.Manager(manager_ports, name=manager_name)
    
    print(f"[manager] Listening on port {manager.port}")
    print(f"[manager] Found {len(matrix_files)} matrix files")

    matrix_pairs = list(itertools.combinations(matrix_files, 2))
    declared_files = {
        path: manager.declare_file(str(path)) for path in matrix_files
    }

    for number, (path_a, path_b) in enumerate(matrix_pairs, start=1):
        task = vine.PythonTask(multiply_matrices, str(path_a), str(path_b))
        task.add_input(declared_files[path_a], str(path_a))
        task.add_input(declared_files[path_b], str(path_b))
        task.set_cores(1)
        manager.submit(task)
        print(
            f"[submit {number:02d}/{len(matrix_pairs)}] "
            f"{path_a.stem} × {path_b.stem}"
        )

    print(f"[manager] Submitted {len(matrix_pairs)} tasks")

    completed_count = 0
    while not manager.empty():
        task = manager.wait(5)
        if not task:
            continue
        if not task.successful() or isinstance(task.output, Exception):
            raise RuntimeError(f"Task {task.id} failed: {task.result}")

        name_a, name_b, shape, norm = task.output
        completed_count += 1
        print(
            f"[done {completed_count:02d}/{len(matrix_pairs)}] "
            f"{name_a} × {name_b} = {shape[0]}×{shape[1]} matrix; "
            f"norm={norm:,.4f}"
        )

    print(f"[manager] Completed all {completed_count} tasks")


if __name__ == "__main__":
    main()
