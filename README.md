# FediRun [![Build Status](https://travis-ci.org/StarlitGhost/FediRun.svg?branch=master)](https://travis-ci.org/StarlitGhost/FediRun) [![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/starlitghost/fedirun.svg)](https://hub.docker.com/r/starlitghost/fedirun) [![Updates](https://pyup.io/repos/github/StarlitGhost/FediRun/shield.svg)](https://pyup.io/repos/github/StarlitGhost/FediRun/) 
A Mastodon bot that runs code in your toots using [tio.run](https://tio.run).

To use, create a config file like this:

```
[fedirun]
class = FediRun.FediRun
domain = mastodon.instance
```

And then run it with `ananas --interactive config.cfg` to set up client secrets and so forth.

See [ananas](https://github.com/chr-1x/ananas) for more details on the bot framework.

# Contributing
Please do! Pull requests are welcome
