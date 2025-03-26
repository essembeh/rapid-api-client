from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel

from rapid_api_client import Query, RapidApi, get, rapid


class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class MainWeatherData(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int


class WindData(BaseModel):
    speed: float
    deg: int
    gust: Optional[float] = None


class CloudsData(BaseModel):
    all: int  # Cloud coverage percentage


class SysData(BaseModel):
    type: Optional[int] = None
    id: Optional[int] = None
    country: str
    sunrise: int
    sunset: int


class CurrentWeather(BaseModel):
    coord: Dict[str, float]
    weather: List[WeatherCondition]
    base: str
    main: MainWeatherData
    visibility: int
    wind: WindData
    clouds: CloudsData
    dt: int
    sys: SysData
    timezone: int
    id: int
    name: str
    cod: int

    def formatted_time(self) -> str:
        """Return a formatted timestamp for the weather data"""
        return datetime.fromtimestamp(self.dt).strftime("%Y-%m-%d %H:%M:%S")


class ForecastItem(BaseModel):
    dt: int
    main: MainWeatherData
    weather: List[WeatherCondition]
    clouds: CloudsData
    wind: WindData
    visibility: int
    pop: float  # Probability of precipitation
    dt_txt: str


class ForecastResponse(BaseModel):
    cod: str
    message: int
    cnt: int
    list: List[ForecastItem]
    city: Dict[str, Any]


@rapid(base_url="https://api.openweathermap.org/data/2.5")
class OpenWeatherMapApi(RapidApi):
    @get("/weather")
    def get_current_weather(
        self,
        q: Annotated[str, Query()],  # City name
        appid: Annotated[str, Query()],  # API key
        units: Annotated[str, Query()] = "metric",  # metric, imperial, standard
        lang: Annotated[str, Query()] = "en",  # Language code
    ) -> CurrentWeather: ...

    @get("/forecast")
    def get_forecast(
        self,
        q: Annotated[str, Query()],  # City name
        appid: Annotated[str, Query()],  # API key
        units: Annotated[str, Query()] = "metric",
        cnt: Annotated[int, Query()] = 40,  # Number of timestamps (max 40)
    ) -> ForecastResponse: ...


def main():
    # You need to provide your OpenWeatherMap API key
    API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

    # Initialize the API client
    api = OpenWeatherMapApi()

    # Get current weather for a city
    try:
        weather = api.get_current_weather(q="London", appid=API_KEY)
        print(f"Current weather in {weather.name}, {weather.sys.country}")
        print(f"Time: {weather.formatted_time()}")
        print(f"Temperature: {weather.main.temp}°C")
        print(f"Feels like: {weather.main.feels_like}°C")
        print(f"Conditions: {weather.weather[0].description}")
        print(f"Wind: {weather.wind.speed} m/s, {weather.wind.deg}°")
        print(f"Humidity: {weather.main.humidity}%")

        # Get 5-day forecast
        forecast = api.get_forecast(
            q="London", appid=API_KEY, cnt=8
        )  # Next 24 hours (3-hour steps)
        print("\nForecast for the next 24 hours:")
        for item in forecast.list:
            print(f"{item.dt_txt}: {item.main.temp}°C, {item.weather[0].description}")

    except Exception as e:
        print(f"Error: {e}")
        print("Note: You need to provide a valid OpenWeatherMap API key")


if __name__ == "__main__":
    main()
