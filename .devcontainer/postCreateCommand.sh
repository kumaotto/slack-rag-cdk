#!/usr/bin/env sh

echo 'Installing Python dependencies with uv...'

# `uv`の自動補完設定
uv completions bash >>~/.bash_completion

# .venvの所有権を変更
sudo chown uv .venv

# 仮想環境をプロジェクト内に作成するように設定
uv config virtualenvs.in-project true

# `uv`で依存関係をインストール
uv install

echo 'Finished postCreateCommand with uv'
