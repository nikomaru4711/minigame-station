# Firebaseランキングの設定

1. Firebase ConsoleでCloud Firestoreのデータベースを作成します。
2. Authentication → ログイン方法で「匿名」を有効にします。
3. `firebase_config.py`の`PROJECT_ID`と`API_KEY`を設定します。現在は空欄です。
4. Firestoreのルールに`firestore.rules`の内容を設定して公開します。

追加のPythonパッケージやサービスアカウント秘密鍵は不要です。
設定が空の間は通信せず、「Firebase未設定」を表示します。名前を入力すればゲームは遊べます。

## 保存形式

| 種別 | コレクション |
| --- | --- |
| ミニゲームアタック | `rankings_attack` |
| イライラ棒 | `rankings_game01` |
| ヲツかぞえ | `rankings_game02` |
| ヲツベーダー | `rankings_game03` |

各ドキュメントのフィールドは以下の３つです。

```json
{
  "player_id": "端末に保存したUUID",
  "player_name": "プレイヤーネーム",
  "score": 628
}
```

ドキュメントIDはFirebase匿名認証のUIDです。同じ認証ユーザーはコレクションごとに
１件しか作成できません。UUID・名前・匿名認証の更新トークンはローカルの
`data/player.json`に保存します。このファイルはGit管理から除外しています。
削除すると別プレイヤーになるため、継続して使う場合は保持してください。

各ゲームの終了時に、そのゲームだけの基本点・ボーナスの合計を送信します。
アタックでも各ゲームの記録を送信し、game03終了時にはアタックの合計も送信します。
０点・部分点も対象です。加点演出の完了を待たず、確定済みの点数を登録します。

同じプレイヤーの既存スコアより高いときだけ更新します。同点・低い記録では、
既存の名前とスコアを維持します。同時更新はFirestoreの更新時刻の条件で検出して再比較します。
ランキングは各コレクションからスコア降順に５件取得します。

通信はゲームループと別のスレッドで行います。通信失敗時はゲームを止めず、
ランキング画面の「更新」で取得と未送信記録の再送を行います。
未送信記録は起動中のメモリに保持されます。再送前にアプリを閉じると失われます。

匿名認証はこの端末の保存情報を引き継ぐ方式です。別端末との同一人物判定や、
クライアントが送信する点数自体の不正検証は行いません。

## 実装の参照資料

- [Cloud Firestore REST API](https://firebase.google.com/docs/firestore/use-rest-api)
- [Firebase Authentication REST API](https://firebase.google.com/docs/reference/rest/auth)
- [ドキュメント更新API](https://firebase.google.com/docs/firestore/reference/rest/v1/projects.databases.documents/patch)
- [更新条件](https://firebase.google.com/docs/firestore/reference/rest/v1/Precondition)

Firebase未設定のため、本番プロジェクトへの接続・ルールのデプロイは行っていません。
