# stella-type-checker

[Online interpreter](https://fizruk.github.io/stella/)

## Setup

```shell
$ pip install -r requirements.txt
$ antlr4 -Dlanguage=Python3 -o src/antlr src/antlr/stellaLexer.g4 src/antlr/stellaParser.g4 -visitor -long-messages
```

## Run

```shell
$ python src/main.py
```

## Test

```shell
$ pytest
```
