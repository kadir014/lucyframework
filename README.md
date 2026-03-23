# lucyframework
<a href="https://github.com/kadir014/lucyframework/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
<img src="https://img.shields.io/badge/python-3.10+-blue">
<img src="https://img.shields.io/badge/version-0.1.1-yellow">

My personal, [pygbag](https://github.com/pygame-web/pygbag)-friendly framework built for [pygame-ce](https://github.com/pygame-community/pygame-ce). Meant to help pygame development, not replace it as an engine.



# Features
- Minimal, well-documented API
- CLI-based quick project initialization (`lucyfw_init`)
- Window and game loop logistics are handled for you
- Built-in entity/scene system with state management
- No event boilerplate - centralized input manager



# Installation
Simply install from PyPI.
```shell
$ pip install lucyframework
```

Run the example project.
```shell
$ lucyfw_example
```

Or initialize a template pygame project in your current directory.
```shell
$ lucyfw_init
```

## » Manual Installation
If you don't or can't download from PyPI.

Clone the repo and `cd` into it.
```shell
$ git clone https://github.com/kadir014/lucyframework.git
```

Build the framework, you can also use `uv`.
```shell
$ python -m pip install .
```

Then you can run the example app to test things out.
```shell
$ python -m lucyfw_example
```


# License
[MIT](LICENSE) © Kadir Aksoy