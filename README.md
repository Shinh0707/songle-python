<a href="https://api.songle.jp">  
  <img src="https://tutorial.songle.jp/images/logos/powered-by-songle-api.png" alt="Powered by Songle" width="250">  
</a>  
  
# Songle API Python Client  
  
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)  
  
Songle API v1 のための Python クライアントライブラリ  
  
これは、楽曲のメタデータや音楽地図情報（拍、コード、メロディ、サビ区間など）を取得するためのインタフェースを提供する、非公式ライブラリです。
  
本ライブラリは以下のAPIを利用しています。  
-   **Songle API**: https://api.songle.jp/  
-   **Songle Widget API**: https://widget.songle.jp/docs/v1   
  
## インストール  
  
現在、このライブラリはPyPIに登録されていません。GitHubリポジトリから直接インストールしてください。  
  
```bash  
pip install git+[https://github.com/](https://github.com/)Shinh0707/songle-python.git  
````  
  
## サンプルコード  
[example.py](example.py)  
  
```python  
from songle import Songle, SongleApiException  
  
# Songleクライアントのインスタンスを作成  
client = Songle()  
  
# 解析したい楽曲のURL  
song_url = "[www.youtube.com/watch?v=PqJNc9KVIZE](https://www.youtube.com/watch?v=PqJNc9KVIZE)"  
  
try:  
  # 1. 楽曲情報を取得  
  print(f"--- 楽曲情報 ---")  
  song = client.get_song_info(song_url)  
  print(f"タイトル: {song.title}")  
  print(f"アーティスト: {song.artist.name}")  
  print(f"楽曲の長さ: {song.duration / 1000:.2f}秒")  
  
  # 2. 拍情報を取得  
  print("\n--- 拍情報 ---")  
  beats = client.get_beats(song_url)  
  if beats.beats:  
    print(f"拍の数: {len(beats.beats)}")  
    # 最初の拍のBPMを表示  
    print(f"BPM (冒頭): {beats.beats[0].bpm}")  
  
  # 3. サビ区間情報を取得  
  print("\n--- サビ区間 ---")  
  chorus = client.get_chorus(song_url)  
  if chorus.chorus_segments:  
    # 最初のサビ区間の情報を表示  
    first_chorus = chorus.chorus_segments[0].repeats[0]  
    start_sec = first_chorus.start / 1000  
    duration_sec = first_chorus.duration / 1000  
    print(f"最初のサビは {start_sec:.2f}秒 から {duration_sec:.2f}秒間")  
  
  # 4. 楽曲を検索  
  print("\n--- 楽曲検索 ---")  
  query = "Tell Your World"  
  search_results = client.search_songs(query)  
  print(f"「{query}」の検索結果: {len(search_results)}件")  
  for s in search_results:  
    print(f"  - {s.title} by {s.artist.name}")  
  
except SongleApiException as e:  
  print(f"\nAPIエラーが発生しました: {e}")  
  
```  
  
## APIリファレンス  
  
`Songle`クラス  
  
### 楽曲情報  
  
  - `get_song_info(url: str) -> Song`  
    - 楽曲のメタデータを取得します。  
  - `search_songs(query: str) -> list[Song]`  
    - キーワードで楽曲を検索します。  
  
### 音楽地図  
  
  - `get_beats(url: str, revision_id: int = None) -> BeatInfo`  
    - 拍情報を取得します。  
  - `get_chords(url: str, revision_id: int = None) -> ChordInfo`  
    - コード情報を取得します。  
  - `get_melody(url: str, revision_id: int = None) -> MelodyInfo`  
    - メロディ情報を取得します。  
  - `get_chorus(url: str, revision_id: int = None) -> ChorusInfo`  
    - サビ区間・繰り返し区間情報を取得します。  
  
### バージョン履歴  
  
  - `get_beat_revisions(url: str) -> list[Revision]`  
  - `get_chord_revisions(url: str) -> list[Revision]`  
  - `get_melody_revisions(url: str) -> list[Revision]`  
  - `get_chorus_revisions(url: str) -> list[Revision]`  
  
## データモデル  
  
APIレスポンスは以下の `dataclass` オブジェクトにマッピングされます。詳細はソースコードを参照してください。  
  
  - `Song`  
  - `Artist`  
  - `Beat` / `BeatInfo`  
  - `Chord` / `ChordInfo`  
  - `Melody` / `MelodyInfo`  
  - `ChorusInfo`  
  - `Revision`  