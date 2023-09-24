# 手順
本アプリを実行する手順を簡単にまとめます。

## 開発コンテナの立ち上げ
Visual Studio Codeの拡張機能であるDev Containerを用います。
コマンドパレットを立ち上げて、`Reopen in Container`と入力して実行してください。

## .envの設定
`.env.sample`を参考にして、`app/backend/.env`と`app/prepdocs/.env`に必要な情報を記載してください。

## LINEのセットアップ
Line Developerの登録を行い、Webhook URLの登録をしてください。
https://developers.line.biz/ja/

## アプリのデプロイ

環境を初期化
```
azd init
```

Azureにログイン
```
azd auth login
```

Azure OpenAIが利用可能なAzureサブスクリプションを設定
```
azd config set defaults.subscription aaaaaaaa-bbbb-cccc-dddddddddddd
```

Azureリソースをプロビジョニング(azd provision)と、アプリのデプロイ(azd deploy)
```
azd up
```

# 注意事項
- Azure Cognitive Searchは高額なので、不要になったらリソースの削除を行うこと。
- Bing検索を使用する場合は、app/backend/app.pyの`use_bing_search`を`True`に変更。さらに、AzureポータルでBingリソースを作成し、BING_API_KEYとBING_ENDPOINTをapp/backend/.envに入力した後、`azd deploy`を実行すること。


# サンプルデータ

デジタル庁「デジタル社会の実現に向けた重点計画」
https://www.digital.go.jp/assets/contents/node/basic_page/field_ref_resources/5ecac8cc-50f1-4168-b989-2bcaabffe870/b24ac613/20230609_policies_priority_outline_05.pdf


# 参考文献

「Azure で ChatGPT × Cognitive Search を使ったエンタープライズサーチを実現」

https://qiita.com/nohanaga/items/803c09b5a3a4e2d1776f

「生成AI用Cognitive Searchの言語アナライザーを日本語にしたい」

https://qiita.com/tmiyata25/items/e8866dfed6dd4b9a02ad

「Azure Container Apps に Flask または FastPI Web アプリをデプロイする」

https://learn.microsoft.com/ja-jp/azure/developer/python/tutorial-containerize-simple-web-app?tabs=web-app-flask

「Docker CLI を使用した、Azure のコンテナー レジストリへの最初のイメージのプッシュ」

https://learn.microsoft.com/ja-jp/azure/container-registry/container-registry-get-started-docker-cli?tabs=azure-cli

「PythonとLINE APIとHerokuで自動返信BOTを作る【Python編】」

https://qiita.com/hy-sksem/items/0e8593d3a3047ece3f77

「PythonとHerokuでLINEBOTを作ってみた」

https://qiita.com/adgjmptw0/items/8c0c99b118a5612f29eb

「Azure Cognitive SearchでBlob上のPDFを検索してみた（Python）」

https://qiita.com/brocolly/items/514a0010f79ffc79adc9

「プロジェクトをAzure Developer CLIと互換性のあるものにする」

https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/make-azd-compatible?pivots=azd-create

「Azure Developer CLIの azure.yaml スキーマ」

https://learn.microsoft.com/ja-jp/azure/developer/azure-developer-cli/azd-schema
