# サーバー監視君

サーバーを監視してLINE BOTで監視内容を送信する  
  
現状送信している情報は
- powershellのGet-Volumeで取得したストレージ利用状況
- CrystalDiskInfoで取得したストレージの健康状態
を適当にまとめたものを画像にしたものです  
  
こんな感じ  
<img src="https://raw.githubusercontent.com/gachuchu/github_images/main/ServerWatchMan/pic00.png?raw=true" width="50%">  
  
## <span style="color:red">免責事項&注意事項</span>

自分の環境・使い方で動けばいいや。で作っているので検証、デバッグが圧倒的に足りていないです。  
本プロジェクトを利用した、または利用できなかった、その他いかなる場合において一切の保障は行いません。  
自己の責任のもとでご利用ください。

## 事前準備

1. LINE DevelopersでMessage APIを使えるようにする。Webhook設定は今回は必須ではないです
1. LINE Developers Consoleの「チャンネル基本設定」で「あなたのユーザID」を取得
1. LINE Developers Consoleの「Message API」で「チャンネルアクセストークン」を取得
1. LINE Developers Consoleの「Message API」のQRコードを読み込んでBOTと友達になる
1. GoogleDriveの適当なフォルダに`smart_summry.png`という名前でダミー画像を設置する
1. GoogleDriveに設置した画像のリンクを「リンクを知っている全員」のアクセス権で取得する
1. CrystalDiskInfoをインストールする

## 使い方
 
1. `python -m venv venv` で作った仮想環境で動かす前提です
1. 仮想環境で`pip install -r requirements.txt`する
1. ServerWatchMan.batの`CRYSTALDISKINFO_PATH`の値を自分の環境にあわせて修正
1. 事前準備で画像を設置したフォルダをServerWatchMan.batの`GOOGLE_DRIVE`に設定する
1. LineConfig.sample.ps1の`channel_access_token`と`to_user_id`の値を事前準備で取得したもので設定する
1. LineConfig.sample.ps1の`message`にLINE Botで画像と一緒に送信するテキストを設定する
1. LineConfig.sample.ps1の`imgurl`にGoogleDriveの画像のリンクを以下ルールで修正して設定する。
	1. 修正前 https://drive.google.com/file/d/*********************************/view?usp=sharing
	1. 修正後 https://drive.google.com/uc?id=*********************************
1. おもむろに`ServerWatchMan.bat`を実行する
1. BOTからメッセージが届いたらおｋ
