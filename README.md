# Distributed Matrix Multiplication — Script Execution

This Floability backpack runs a distributed TaskVine matrix workflow as a
Python script. It demonstrates the same portable software, data, and compute
specifications as the notebook-based matrix example, but uses
`floability execute` so no Jupyter server, browser, or SSH tunnel is required.

The backpack stages ten dense 200×200 matrices from the public
`floability/backpack-test-data` repository. The workflow submits one TaskVine
`PythonTask` for every unique pair, multiplies the matrices, computes the
Frobenius norm of each result, and prints each result in the terminal as it
finishes.

```text
10 matrices → 45 distributed tasks → results printed in the terminal
```

## Backpack contents

```text
matrix-multiplication-script/
├── compute/
│   └── compute.yml
├── data/
│   └── data.yml
├── software/
│   └── environment.yml
└── workflow/
    └── matrix-multiplication-script.py
```

- `workflow/matrix-multiplication-script.py` defines the TaskVine manager,
  submits the matrix tasks, and prints their results.
- `software/environment.yml` pins the Python, NumPy, and TaskVine software.
- `data/data.yml` downloads, stages, and strictly verifies all ten matrices
  from their public remote sources.
- `compute/compute.yml` requests 2–4 local workers with one core each.

## Install Floability

Follow the
[Floability installation guide](https://floability.readthedocs.io/en/stable/getting-started/installation/),
then verify the command is available:

```bash
floability --version
```

## Validate the backpack

From the repository root:

```bash
floability backpack validate --strict .
```

## Execute the workflow

```bash
floability execute \
  --backpack . \
  --entrypoint matrix-multiplication-script.py
```

Floability will:

1. prepare and cache the backpack's Conda environment;
2. download, verify, cache, and stage the remote matrix data;
3. start the TaskVine workers described by `compute/compute.yml`;
4. execute the Python workflow while streaming each result to the terminal.

No Jupyter server is started. The complete script output is also retained in
the Floability instance log at `logs/workflow.log`.

## Confirm success

A successful execution reports:

```text
[manager] Found 10 matrix files
[submit 01/45] matrix_dense_00 × matrix_dense_01
...
[manager] Submitted 45 tasks
...
[done 01/45] matrix_dense_00 × matrix_dense_01 = 200×200 matrix; norm=93,676.2841
...
[manager] Completed all 45 tasks
```

## Run it again

Run the same command a second time:

```bash
floability execute \
  --backpack . \
  --entrypoint matrix-multiplication-script.py
```

The workflow result is recomputed, but Floability can reuse the prepared
software environment and downloaded data cache. This separates repeatable
workflow execution from one-time environment and data preparation.

## Other execution sites

Use the same backpack with an available batch system:

```bash
floability execute \
  --backpack . \
  --entrypoint matrix-multiplication-script.py \
  --batch-type slurm
```

Replace `slurm` with `condor` or `uge` when appropriate. The selected batch
system must already be installed and configured at the execution site.
