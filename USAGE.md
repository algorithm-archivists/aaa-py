# AAA-py CLI usage guide

The CLI for the AAA-py is (for now) based on Make and pipenv.

## Oneline use (easy)

To setup the dependencies properly, make sure that the Python and git2 development headers are available in your `PATH`.

One this is done, simply run `make`, and the website will be available at http://localhost:8080once building is completed (provided the 8080 port is available for the spawned server).

## Advanced setup

1. To only install the Python packages dependencies, run `make install`.

2. To only build the website (using the latest upstream contents from the AAA), run `make build`

3. To build the website (using already-present contents, without fetching from upstream), run `make build_local`

4. To spawn the file server, run `make serve`

## Additional build target

1. `local`: `make local` will run the `build_local` and `serve` targets.
Do **NOT** use `make local` at first use, since this `build_local` requires that the contents are already presents.
