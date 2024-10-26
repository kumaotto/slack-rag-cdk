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

echo 'Finished installing Python dependencies with uv'

# Git Secretsのインストールとセットアップ
echo 'Installing Git Secrets...'

git config --global --add safe.directory /workspace
git clone https://github.com/awslabs/git-secrets.git
cd git-secrets || exit
sudo make install
cd ..
rm -rf git-secrets # クローンしたディレクトリを削除
git secrets --install
git secrets --register-aws

echo 'Finished postCreateCommand with Git Secrets setup'
