# Raspberry Pi


## 連絡事項
mysql の video テーブルの status について
1: 配信予定
2: 配信中
3: 配信終了
4: ただの動画
5: メンバー限定
6: 存在しない

notified & 64 : 編集者への通知

analysis_status
1: 未解析
2: 未解析（後でもう一度聞いてみる）
3: 解析中
4: 解析完了
5: エラー


## Raspberry Pi
再起動時にファイルチェック：`shutdown -r -F now`<br>
アップデートする。
```
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
```
`sudo apt install`<br>
mysql
firefox-esr
python3-pip


## Cron
`service cron status`<br>
### 設定する
`crontab -e`<br>
追記する：`0 * * * * sh ---.sh`<br>
追記する：`@reboot sh ---.sh`<br>
### 設定を確認する
`crontab -l`<br>
### ログ
`vi /etc/rsyslog.conf`<br>
60行目くらいの`#cron.* ...`の`#`を削除する。<br>
`sudo service rsyslog restart`<br>
ログファイル：`/var/log/cron.log`<br>

## MySQL

### インストール
`sudo apt-get install mysql-server`<br>
ルートユーザのパスワードを設定する。

### 起動・停止
`(sudo) service mysql start`<br>
`(sudo) service mysql stop`<br>
`(sudo) service mysql restart`<br>
`service mysql status`<br>
`(sudo) /etc/init.d/mysql start`<br>
`(sudo) /etc/init.d/mysql stop`<br>
`(sudo) /etc/init.d/mysql restart`<br>
`/etc/init.d/mysql status`<br>

### ログイン
ルートユーザでのログイン：`mysql -u root -p`

### 文字コード

#### 確認
`mysql> status`<br>
`mysql> show variables like '%char%';`<br>
`mysql> show variables like "chara%";`<br>

#### 変更
`/etc/mysql/my.cnf` に追記する。
```
[client]
default-character-set = utf8
[mysqld]
character-set-server = utf8
```

### メモ
実行したコマンドを書いていく。
```
show databases;
CREATE DATABASE vcdb_rp;
USE vcdb_rp;

CREATE TABLE vtuber (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(256),
    youtube_channel_id VARCHAR(64)
);
CREATE TABLE video (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    vtuber_id INT UNSIGNED,
    status TINYINT UNSIGNED NOT NULL DEFAULT 0,
    title VARCHAR(256),
    youtube_video_id VARCHAR(64),
    start DATETIME,
    end DATETIME,
    notified TINYINT UNSIGNED NOT NULL DEFAULT 0,
    analysis_status TINYINT UNSIGNED NOT NULL DEFAULT 0,
    analysis_result VARCHAR(1024)
);

ALTER TABLE (table) ADD (column) INT AFTER (column);
ALTER TABLE (table) MODIFY (column) INT NOT NULL DEFAULT 0;

show tables;
desc (table);

INSERT INTO vtuber(name, youtube_channel_id) VALUES
    ('早瀬 走', 'UC2OacIzd2UxGHRGhdHl1Rhw'),
    ('白雪 巴', 'UCuvk5PilcvDECU7dDZhQiEw');

UPDATE vtuber SET name=" ... ", youtube_channel_id=" ... " WHERE id=1;

CREATE USER '(username)'@'(host)' IDENTIFIED BY '(password)';
    (host) : localhost, % (どこからでもアクセス), ...

ユーザ一覧
SELECT host, user FROM mysql.user;

権限
show grants for '(username)'@'(host)'
GRANT SELECT (id, name, ...), INSERT, UPDATE ON vcdb_rp.vtuber TO '(username)'@'(host)' IDENTIFIED BY '(password)';




```


## Python

### インストール
最新バージョンは、自分でインストールする。
```
wget (URL)
tar -xvf (.tar.xz file) -C (解凍先ディレクトリ)
cd (dir)
./configure
make
sudo make altinstall
```

### ライブラリ
`sudo pip3.9 install ...`<br>
selenium
beautifulsoup4
mysql-connector-python
requests
datetime
flask

## 参考

### python
https://qiita.com/GuitarBuilderClass/items/d6d2798bebf7b916c5c6

### selenium
https://sun0range.com/information-technology/raspberry-pi-selenium

