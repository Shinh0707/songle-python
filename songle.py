"""
Songle Rest API (version 1) を使用
 ・https://api.songle.jp/
 ・https://widget.songle.jp/docs/v1
"""

import dataclasses
import re
from typing import Any, Optional, Type, TypeVar

import requests

# Generic type variable for dataclass models.
T = TypeVar("T")


class SongleApiException(Exception):
    """Custom exception for Songle API errors.

    Attributes:
        status_code: The HTTP status code of the error response.
        message: The error message.
    """

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"[{status_code}] {message}")


# Data models for API responses.
@dataclasses.dataclass(frozen=True)
class Artist:
    """Represents an artist."""
    id: int
    name: str


@dataclasses.dataclass(frozen=True)
class Song:
    """Represents a song's metadata."""
    id: int
    title: str
    url: str
    permalink: str
    artist: Artist
    duration: float
    code: str
    rms_amplitude: float
    created_at: str
    updated_at: str
    recognized_at: str


@dataclasses.dataclass(frozen=True)
class Beat:
    """Represents a single beat in the beat map."""
    index: int
    start: int
    count: int
    position: int
    bpm: int


@dataclasses.dataclass(frozen=True)
class BeatInfo:
    """Represents a collection of beats."""
    beats: list[Beat]


@dataclasses.dataclass(frozen=True)
class Revision:
    """Represents a version of a musical map."""
    id: int
    created_at: str
    updated_at: str


@dataclasses.dataclass(frozen=True)
class Chord:
    """Represents a single chord in the chord map."""
    index: int
    start: int
    duration: int
    name: str


@dataclasses.dataclass(frozen=True)
class ChordInfo:
    """Represents a collection of chords."""
    chords: list[Chord]


@dataclasses.dataclass(frozen=True)
class Note:
    """Represents a single note in the melody map."""
    index: int
    start: int
    duration: int


@dataclasses.dataclass(frozen=True)
class MelodyInfo:
    """Represents a collection of notes."""
    notes: list[Note]


@dataclasses.dataclass(frozen=True)
class Repeat:
    """Represents a repeated section."""
    index: int
    start: int
    duration: int


@dataclasses.dataclass(frozen=True)
class ChorusSegment:
    """Represents a chorus segment."""
    index: int
    is_chorus: bool
    duration: int
    repeats: list[Repeat]


@dataclasses.dataclass(frozen=True)
class RepeatSegment:
    """Represents a general repeated segment."""
    index: int
    is_chorus: bool
    duration: int
    repeats: list[Repeat]


@dataclasses.dataclass(frozen=True)
class ChorusInfo:
    """Represents chorus and repeat segment information."""
    chorus_segments: list[ChorusSegment]
    repeat_segments: list[RepeatSegment]


def _to_snake_case(name: str) -> str:
    """Converts a camelCase string to snake_case.

    Args:
        name: The string in camelCase format.

    Returns:
        The converted string in snake_case format.
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _convert_keys_to_snake_case(data: Any) -> Any:
    """Recursively converts dictionary keys from camelCase to snake_case.

    Args:
        data: A dictionary, list, or other value.

    Returns:
        The data structure with all dictionary keys converted to snake_case.
    """
    if isinstance(data, dict):
        return {
            _to_snake_case(k): _convert_keys_to_snake_case(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [_convert_keys_to_snake_case(i) for i in data]
    return data

def _from_dict(model: Type[T], data: dict[str, Any]) -> T:
    """Instantiates a dataclass from a dictionary, handling nested models.

    Args:
        model: The dataclass type to instantiate.
        data: The dictionary containing the data.

    Returns:
        An instance of the specified dataclass.
        
    Raises:
        TypeError: If the provided model is not a dataclass.
    """
    if not dataclasses.is_dataclass(model):
        raise TypeError(f"Expected a dataclass type, but got {model}.")

    field_types = {f.name: f.type for f in dataclasses.fields(model)}
    kwargs = {}
    for name, value in data.items():
        if name not in field_types:
            continue

        field_type = field_types[name]
        origin = getattr(field_type, "__origin__", None)
        args = getattr(field_type, "__args__", ())

        if origin is list and args and dataclasses.is_dataclass(args[0]):
            element_type = args[0]
            if isinstance(value, list):
                kwargs[name] = [_from_dict(element_type, item) for item in value]
        
        # 'field_type'が「型」であることを保証する条件を追加
        elif isinstance(field_type, type) and dataclasses.is_dataclass(field_type):
            if isinstance(value, dict):
                kwargs[name] = _from_dict(field_type, value)
        else:
            kwargs[name] = value

    return model(**kwargs)

class Songle:
    """A client for interacting with the Songle API."""

    _BASE_URL: str = "https://widget.songle.jp/"

    def __init__(self, session: Optional[requests.Session] = None) -> None:
        """Initializes the Songle API client.

        Args:
            session: An optional requests.Session object to use for making
              HTTP requests. If not provided, a new session will be created.
        """
        self._session = session or requests.Session()

    def _build_url(self, path: str) -> str:
        """Constructs a full URL for an API endpoint.

        Args:
            path: The relative path of the API endpoint.

        Returns:
            The absolute URL for the endpoint.
        """
        return f"{self._BASE_URL}{path}"

    def _get(
        self,
        path: str,
        params: Optional[dict[str, Any]] = None,
    ) -> Any:
        """Performs a GET request to the specified API endpoint.

        Args:
            path: The relative path of the API endpoint.
            params: A dictionary of query parameters for the request.

        Returns:
            The JSON response from the API as a dictionary or list.

        Raises:
            SongleApiException: If the API returns a non-200 status code.
        """
        url = self._build_url(path)
        try:
            response = self._session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_message = f"Error response from API: {e.response.text}"
            raise SongleApiException(
                status_code=e.response.status_code, message=error_message
            ) from e
        except requests.exceptions.RequestException as e:
            raise SongleApiException(
                status_code=500, message=f"Request failed: {e}"
            ) from e

    def _fetch_and_parse(
        self,
        path: str,
        model: Type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> T:
        """Fetches data from an endpoint and parses it into a dataclass model.

        Args:
            path: The relative path of the API endpoint.
            model: The dataclass to parse the response into.
            params: A dictionary of query parameters for the request.

        Returns:
            An instance of the specified dataclass model.
        """
        raw_data = self._get(path, params=params)
        converted_data = _convert_keys_to_snake_case(raw_data)
        return _from_dict(model, converted_data)

    def _fetch_and_parse_list(
        self,
        path: str,
        model: Type[T],
        params: Optional[dict[str, Any]] = None,
    ) -> list[T]:
        """Fetches data from an endpoint and parses it into a list of dataclass models.

        Args:
            path: The relative path of the API endpoint.
            model: The dataclass to parse each item of the list into.
            params: A dictionary of query parameters for the request.

        Returns:
            A list of instances of the specified dataclass model.
        """
        raw_data = self._get(path, params=params)
        converted_data = _convert_keys_to_snake_case(raw_data)
        return [_from_dict(model, item) for item in converted_data]

    def get_song_info(self, url: str) -> Song:
        """Retrieves information about a song.

        Args:
            url: The URL of the song on the source website.

        Returns:
            A Song object containing the song's metadata.
        """
        return self._fetch_and_parse(
            "api/v1/song.json", Song, params={"url": url}
        )

    def get_beats(
        self, url: str, revision_id: Optional[int] = None
    ) -> BeatInfo:
        """Retrieves the beat map for a song.

        Args:
            url: The URL of the song on the source website.
            revision_id: The version ID of the musical map.

        Returns:
            A BeatInfo object containing the beat map.
        """
        params = {"url": url}
        if revision_id is not None:
            params["revision_id"] = str(revision_id)
        return self._fetch_and_parse("api/v1/song/beat.json", BeatInfo, params)

    def get_beat_revisions(self, url: str) -> list[Revision]:
        """Retrieves the list of beat map versions for a song.

        Args:
            url: The URL of the song on the source website.

        Returns:
            A list of Revision objects.
        """
        return self._fetch_and_parse_list(
            "api/v1/song/beat_revisions.json", Revision, params={"url": url}
        )

    def get_chords(
        self, url: str, revision_id: Optional[int] = None
    ) -> ChordInfo:
        """Retrieves the chord map for a song.

        Args:
            url: The URL of the song on the source website.
            revision_id: The version ID of the musical map.

        Returns:
            A ChordInfo object containing the chord map.
        """
        params = {"url": url}
        if revision_id is not None:
            params["revision_id"] = str(revision_id)
        return self._fetch_and_parse("api/v1/song/chord.json", ChordInfo, params)

    def get_chord_revisions(self, url: str) -> list[Revision]:
        """Retrieves the list of chord map versions for a song.

        Args:
            url: The URL of the song on the source website.

        Returns:
            A list of Revision objects.
        """
        return self._fetch_and_parse_list(
            "api/v1/song/chord_revisions.json", Revision, params={"url": url}
        )

    def get_melody(
        self, url: str, revision_id: Optional[int] = None
    ) -> MelodyInfo:
        """Retrieves the melody map for a song.

        Args:
            url: The URL of the song on the source website.
            revision_id: The version ID of the musical map.

        Returns:
            A MelodyInfo object containing the melody map.
        """
        params = {"url": url}
        if revision_id is not None:
            params["revision_id"] = str(revision_id)
        return self._fetch_and_parse("api/v1/song/melody.json", MelodyInfo, params)

    def get_melody_revisions(self, url: str) -> list[Revision]:
        """Retrieves the list of melody map versions for a song.

        Args:
            url: The URL of the song on the source website.

        Returns:
            A list of Revision objects.
        """
        return self._fetch_and_parse_list(
            "api/v1/song/melody_revisions.json", Revision, params={"url": url}
        )

    def get_chorus(
        self, url: str, revision_id: Optional[int] = None
    ) -> ChorusInfo:
        """Retrieves the chorus map for a song.

        Args:
            url: The URL of the song on the source website.
            revision_id: The version ID of the musical map.

        Returns:
            A ChorusInfo object containing the chorus map.
        """
        params = {"url": url}
        if revision_id is not None:
            params["revision_id"] = str(revision_id)
        return self._fetch_and_parse("api/v1/song/chorus.json", ChorusInfo, params)

    def get_chorus_revisions(self, url: str) -> list[Revision]:
        """Retrieves the list of chorus map versions for a song.

        Args:
            url: The URL of the song on the source website.

        Returns:
            A list of Revision objects.
        """
        return self._fetch_and_parse_list(
            "api/v1/song/chorus_revisions.json", Revision, params={"url": url}
        )

    def search_songs(self, query: str) -> list[Song]:
        """Searches for songs.

        Args:
            query: The search string.

        Returns:
            A list of Song objects matching the search query.
        """
        return self._fetch_and_parse_list(
            "api/v1/songs/search.json", Song, params={"q": query}
        )