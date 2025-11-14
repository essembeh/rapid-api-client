from datetime import date, timedelta
from typing import Annotated, List, Optional

from pydantic import BaseModel, HttpUrl

from rapid_api_client import Query, RapidApi, get, rapid_default


class AstronomyPicture(BaseModel):
    date: str
    explanation: str
    hdurl: Optional[HttpUrl] = None
    media_type: str
    service_version: str
    title: str
    url: HttpUrl
    copyright: Optional[str] = None


class NeoObject(BaseModel):
    id: str
    name: str
    nasa_jpl_url: HttpUrl
    absolute_magnitude_h: float
    estimated_diameter: dict
    is_potentially_hazardous_asteroid: bool
    close_approach_data: List[dict]
    is_sentry_object: bool


class NeoResponse(BaseModel):
    element_count: int
    near_earth_objects: dict  # Keys are dates, values are lists of NeoObject


class MarsRoverPhoto(BaseModel):
    id: int
    sol: int
    camera: dict
    img_src: HttpUrl
    earth_date: str
    rover: dict


class MarsRoverPhotosResponse(BaseModel):
    photos: List[MarsRoverPhoto]


@rapid_default(base_url="https://api.nasa.gov")
class NasaApi(RapidApi):
    @get("/planetary/apod")
    def get_astronomy_picture(
        self,
        api_key: Annotated[str, Query()],
        date: Annotated[Optional[str], Query()] = None,
        start_date: Annotated[Optional[str], Query()] = None,
        end_date: Annotated[Optional[str], Query()] = None,
        count: Annotated[Optional[int], Query()] = None,
        thumbs: Annotated[bool, Query()] = False,
    ) -> AstronomyPicture | List[AstronomyPicture]: ...

    @get("/neo/rest/v1/feed")
    def get_asteroids(
        self,
        api_key: Annotated[str, Query()],
        start_date: Annotated[str, Query()],
        end_date: Annotated[Optional[str], Query()] = None,
    ) -> NeoResponse: ...

    @get("/mars-photos/api/v1/rovers/curiosity/photos")
    def get_mars_rover_photos(
        self,
        api_key: Annotated[str, Query()],
        sol: Annotated[Optional[int], Query()] = None,
        earth_date: Annotated[Optional[str], Query()] = None,
        camera: Annotated[Optional[str], Query()] = None,
        page: Annotated[int, Query()] = 1,
    ) -> MarsRoverPhotosResponse: ...


def main():
    # You need to provide your NASA API key
    # You can get a free API key at https://api.nasa.gov/
    API_KEY = "DEMO_KEY"  # Replace with your actual API key or use DEMO_KEY for limited access

    # Initialize the API client
    api = NasaApi()

    try:
        # Get today's Astronomy Picture of the Day
        print("NASA Astronomy Picture of the Day (APOD):")
        apod = api.get_astronomy_picture(api_key=API_KEY)
        if isinstance(apod, list):
            apod = apod[0]  # In case the API returns a list

        print(f"Title: {apod.title}")
        print(f"Date: {apod.date}")
        if apod.copyright:
            print(f"Copyright: {apod.copyright}")
        print(f"Media Type: {apod.media_type}")
        print(f"URL: {apod.url}")
        print(f"Explanation: {apod.explanation[:150]}...")  # Truncated for brevity

        # Get last week's APODs
        today = date.today()
        week_ago = today - timedelta(days=7)
        print(f"\nAPODs from the last week ({week_ago} to {today}):")

        weekly_apods = api.get_astronomy_picture(
            api_key=API_KEY,
            start_date=week_ago.isoformat(),
            end_date=today.isoformat(),
        )

        if isinstance(weekly_apods, list):
            for i, apod in enumerate(weekly_apods, 1):
                print(f"{i}. {apod.date}: {apod.title}")

        # Get information about near-Earth objects (asteroids)
        print("\nNear-Earth Objects (Asteroids) approaching Earth today:")
        today_str = today.isoformat()
        neo_response = api.get_asteroids(api_key=API_KEY, start_date=today_str)

        if today_str in neo_response.near_earth_objects:
            asteroids = neo_response.near_earth_objects[today_str]
            print(f"Found {len(asteroids)} asteroids approaching Earth today")

            for i, asteroid in enumerate(asteroids[:3], 1):  # Show only first 3
                hazardous = (
                    "🚨 POTENTIALLY HAZARDOUS"
                    if asteroid.is_potentially_hazardous_asteroid
                    else "Safe"
                )
                print(f"{i}. {asteroid.name} - {hazardous}")

                if asteroid.close_approach_data:
                    approach = asteroid.close_approach_data[0]
                    distance_km = float(approach["miss_distance"]["kilometers"])
                    velocity_kph = float(
                        approach["relative_velocity"]["kilometers_per_hour"]
                    )
                    print(f"   Miss Distance: {distance_km:,.0f} km")
                    print(f"   Velocity: {velocity_kph:,.0f} km/h")

                min_diameter = asteroid.estimated_diameter["kilometers"][
                    "estimated_diameter_min"
                ]
                max_diameter = asteroid.estimated_diameter["kilometers"][
                    "estimated_diameter_max"
                ]
                print(
                    f"   Estimated Diameter: {min_diameter:.2f} - {max_diameter:.2f} km"
                )

        # Get Mars Rover photos
        print("\nLatest Mars Curiosity Rover Photos:")
        mars_photos = api.get_mars_rover_photos(api_key=API_KEY, page=1)

        for i, photo in enumerate(mars_photos.photos[:3], 1):  # Show only first 3
            print(f"{i}. Photo ID: {photo.id}")
            print(f"   Earth Date: {photo.earth_date}")
            print(f"   Camera: {photo.camera['full_name']} ({photo.camera['name']})")
            print(f"   URL: {photo.img_src}")

    except Exception as e:
        print(f"Error: {e}")
        print(
            "Note: Using DEMO_KEY has strict rate limits. Get your own API key at https://api.nasa.gov/"
        )


if __name__ == "__main__":
    main()
