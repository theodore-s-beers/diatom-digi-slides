# diatom-digi-slides

```sh
uv sync --all-extras
```

```sh
source .venv/bin/activate
```

```sh
pex . -m diatom_digi_slides.one_slide -o one_slide.pex
```

This last command will build a `one_slide.pex` executable, which can be moved
anywhere and run anywhere.

There are, however, a few prerequisites to run the program:

- A Java installation (I've been using `openjdk-17-jre-headless`)
- Maven
- `bioformats2raw` in PATH
- `raw2ometiff` in PATH
