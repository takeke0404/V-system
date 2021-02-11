# v_xxxx

v_xxxx ファイルについての説明を書きます。

## v_cron.py
`python v_cron.py 1` selenium を使う
`python v_cron.py 2` selenium を使わない

## v_scraper.py

### def youtube_channel(driver, チャンネルID)
YouTubeチャンネルから今後の配信予定を取得します。<br>
@return 動画IDのセット or 空セット<br>

### def youtube_embedded_live(チャンネルID)
ライブ配信埋め込みURLから一番近い配信予定の動画を取得します。<br>
@return 動画ID or None<br>

### def youtube_video(動画ID)
動画の情報を取得します。<br>
@return ステータス, タイトル, 開始時刻, 終了時刻, 動画説明に存在するYouTubeチャンネルへのリンクのセット（自身のチャンネルを含む可能性あり）, チャットが存在するか<br>

## v_mler.py

### def analyze_next()
未解析動画を解析します。
