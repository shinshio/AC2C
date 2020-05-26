<img src="./docs/images/logo/car_dekotora.ico">
<img src="./docs/images/logo/car_dekotora.ico">

# Index

<!-- TOC -->

- [Index](#index)
- [Description](#description)
- [Feature](#feature)
- [Requirement](#requirement)
- [Installation](#installation)
- [Usage](#usage)
- [Note](#note)
- [Author](#author)
- [Licence](#licence)

<!-- /TOC -->

# Description

これはAutoChecker2をWindowsから操作するスクリプトです。

本READMEで、環境作成～スクリプト実行までを説明します。

>python(pyenv), pipenv の準備は別を参照してね。

2020年6月リリースのAutoChecker2の操作スクリプトです。

このスクリプトは以下の使用を前提に成り立っています。

1. 別エクセルマクロで作成されたシナリオを読み込み、指示通り実行する。
2. シナリオ以外でも、各コマンドを使用して内部リレーを制御できる。
3. 上記を単純な使用法で実現する。

以上を満たすため、本スクリプトは以下の構成で実現しました。

- 言語：Python 3.7.5
- GUIツール：Qt5
- チェッカ通信：USBを使用したシリアル通信
- シナリオ：エクセルファイル(マクロから出力)

# Feature

- 完全OSS。
- その気になれば全OEM向けに使用できるはず。
- 超協力的に横展開します。何なりと申しつけください。(From author)
- 極力シナリオから操作できるよう配慮したつもり。
- ハードも自作で安い。~~きれいとは言っていない。~~

# Requirement

- Python: 3.7.5 ※PyInstallerの対応バージョンによる
- pyenv: 1.2.4
- pipenv: 2018.11.26
- modules: `Pipfile`, `Pipfile.lock` を参照
- git: 2.26.2.windows.1

# Installation

>Python, pipenv は各自インストール済みであること。

1. このフォルダを適当な場所にローカルコピーする。フォルダ名にスペースを使用しないこと。
2. `cmd`で以下のとおり環境構築する。

    ```cmd
    mkdir your_project_folder
    xcopy /e this_folder your_project_folder
    cd your_project_folder
    pipenv install
    ```

3. ローカルコピーしたフォルダを削除する。
   ```cmd
   rd /s this_folder
   ```

# Usage

PythonがインストールされていないPC

>1. 配布用zipを適当な場所にダウンロードする。
>2. zipを好きな場所に解凍する。(最近は展開と呼ぶらしい)
>3. 解凍されたフォルダ内の「ACC.exe」を実行する。
>4. チェッカとPCをUSBで接続する。

Python, pipenvがインストールされているPC

>1. 用意したフォルダに入る
>2. `pipenv run run`

# Note

何も知らない人でも使えるよう配慮したつもりです。

ソース改造等自由にして頂いて結構ですが、そういった設計思想は継承して頂けると幸いです。

# Author

- shinshio
- [![TOTEC AMENITY LIMITED](docs/images/logo/totecamenity.png)](https://www.totec.jp/)
- shintaro.shiono.j4j@densotechno.com
- In DENSO, since 2014.5.6
- In charge of Truck

# Licence

COMPLETELY FREE !!!<br>
No need any contact to use !!!
