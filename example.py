from songle import Songle, SongleApiException

def main() -> None:
    """
    A simple demonstration of the Songle API client.
    """
    client = Songle()
    song_url = "www.youtube.com/watch?v=PqJNc9KVIZE"
    search_query = "Tell Your World"

    try:
        # 1. 楽曲情報の取得
        print(f"--- Fetching song info for URL: {song_url} ---")
        song = client.get_song_info(song_url)
        print(f"Title: {song.title}")
        print(f"Artist: {song.artist.name}")
        print("-" * 20)

        # 2. 拍情報の取得
        print("--- Fetching beat map ---")
        beats_info = client.get_beats(song_url)
        if beats_info.beats:
            first_beat = beats_info.beats[0]
            print(f"Found {len(beats_info.beats)} beats.")
            print(f"First beat starts at {first_beat.start}ms with BPM {first_beat.bpm}")
        print("-" * 20)
        
        # 3. コード情報の取得
        print("--- Fetching chord map ---")
        chords_info = client.get_chords(song_url)
        if chords_info.chords:
            first_chord = chords_info.chords[1] # Index 0 is often 'N' (No Chord)
            print(f"Found {len(chords_info.chords)} chords.")
            print(f"First actual chord is '{first_chord.name}' at {first_chord.start}ms")
        print("-" * 20)
        
        # 4. サビ区間情報の取得
        print("--- Fetching chorus info ---")
        chorus_info = client.get_chorus(song_url)
        if chorus_info.chorus_segments:
            first_chorus = chorus_info.chorus_segments[0]
            print(f"Found {len(first_chorus.repeats)} chorus sections.")
            first_repeat = first_chorus.repeats[0]
            print(f"First chorus starts at {first_repeat.start}ms, duration {first_repeat.duration}ms")
        print("-" * 20)

        # 5. 楽曲検索
        print(f"--- Searching for songs with query: '{search_query}' ---")
        search_results = client.search_songs(search_query)
        print(f"Found {len(search_results)} results.")
        for found_song in search_results:
            print(f"  - {found_song.title} by {found_song.artist.name}")

    except SongleApiException as e:
        print(f"An API error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()