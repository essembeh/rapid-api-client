from datetime import datetime
from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel

from rapid_api_client import Path, Query, RapidApi, get, rapid


class CoinMarketData(BaseModel):
    current_price: Dict[str, float]
    market_cap: Dict[str, float]
    total_volume: Dict[str, float]
    price_change_percentage_24h: Optional[float] = None
    price_change_percentage_7d: Optional[float] = None
    price_change_percentage_30d: Optional[float] = None


class CoinImage(BaseModel):
    thumb: str
    small: str
    large: str


class CoinDetail(BaseModel):
    id: str
    symbol: str
    name: str
    description: Optional[Dict[str, str]] = None
    image: Optional[CoinImage] = None
    market_data: Optional[CoinMarketData] = None
    last_updated: Optional[str] = None


class SimpleCoin(BaseModel):
    id: str
    symbol: str
    name: str
    image: Optional[str] = None
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    market_cap_rank: Optional[int] = None
    price_change_percentage_24h: Optional[float] = None


class GlobalData(BaseModel):
    active_cryptocurrencies: int
    markets: int
    total_market_cap: Dict[str, float]
    total_volume: Dict[str, float]
    market_cap_percentage: Dict[str, float]
    market_cap_change_percentage_24h_usd: float
    updated_at: int


class GlobalResponse(BaseModel):
    data: GlobalData


@rapid(base_url="https://api.coingecko.com/api/v3")
class CoinGeckoApi(RapidApi):
    @get("/coins/markets")
    def get_coin_markets(
        self,
        vs_currency: Annotated[str, Query()] = "usd",
        ids: Annotated[
            Optional[str], Query()
        ] = None,  # Comma-separated list of coin IDs
        order: Annotated[str, Query()] = "market_cap_desc",
        per_page: Annotated[int, Query()] = 100,
        page: Annotated[int, Query()] = 1,
        sparkline: Annotated[bool, Query()] = False,
        price_change_percentage: Annotated[Optional[str], Query()] = None,
    ) -> List[SimpleCoin]: ...

    @get("/coins/{id}")
    def get_coin_details(
        self,
        id: Annotated[str, Path()],
        localization: Annotated[bool, Query()] = False,
        tickers: Annotated[bool, Query()] = False,
        market_data: Annotated[bool, Query()] = True,
        community_data: Annotated[bool, Query()] = False,
        developer_data: Annotated[bool, Query()] = False,
    ) -> CoinDetail: ...

    @get("/global")
    def get_global_data(self) -> GlobalResponse: ...


def main():
    # Initialize the API client
    api = CoinGeckoApi()

    try:
        # Get global market data
        global_data = api.get_global_data()
        print("Global Cryptocurrency Market Data:")
        print(f"Active Cryptocurrencies: {global_data.data.active_cryptocurrencies}")
        print(f"Active Markets: {global_data.data.markets}")
        print(
            f"Total Market Cap (USD): ${global_data.data.total_market_cap.get('usd', 0):,.2f}"
        )
        print(
            f"Total 24h Volume (USD): ${global_data.data.total_volume.get('usd', 0):,.2f}"
        )
        print(
            f"BTC Dominance: {global_data.data.market_cap_percentage.get('btc', 0):.2f}%"
        )
        print(
            f"ETH Dominance: {global_data.data.market_cap_percentage.get('eth', 0):.2f}%"
        )
        print(
            f"Last Updated: {datetime.fromtimestamp(global_data.data.updated_at).strftime('%Y-%m-%d %H:%M:%S')}"
        )

        # Get top 5 cryptocurrencies by market cap
        print("\nTop 5 Cryptocurrencies by Market Cap:")
        coins = api.get_coin_markets(vs_currency="usd", per_page=5, page=1)
        for i, coin in enumerate(coins, 1):
            print(f"{i}. {coin.name} ({coin.symbol.upper()})")
            print(f"   Price: ${coin.current_price:,.2f}")
            print(f"   Market Cap: ${coin.market_cap:,.2f}")
            print(f"   24h Change: {coin.price_change_percentage_24h:.2f}%")

        # Get detailed information about Bitcoin
        print("\nBitcoin Details:")
        bitcoin = api.get_coin_details("bitcoin")
        print(f"Name: {bitcoin.name} ({bitcoin.symbol.upper()})")
        if bitcoin.description and "en" in bitcoin.description:
            description = (
                bitcoin.description["en"].split(". ")[0] + "."
            )  # First sentence only
            print(f"Description: {description}")
        if bitcoin.market_data:
            print(
                f"Current Price (USD): ${bitcoin.market_data.current_price.get('usd', 0):,.2f}"
            )
            print(
                f"Market Cap (USD): ${bitcoin.market_data.market_cap.get('usd', 0):,.2f}"
            )
            print(
                f"24h Volume (USD): ${bitcoin.market_data.total_volume.get('usd', 0):,.2f}"
            )
            if bitcoin.market_data.price_change_percentage_24h:
                print(
                    f"24h Change: {bitcoin.market_data.price_change_percentage_24h:.2f}%"
                )
            if bitcoin.market_data.price_change_percentage_7d:
                print(
                    f"7d Change: {bitcoin.market_data.price_change_percentage_7d:.2f}%"
                )

    except Exception as e:
        print(f"Error: {e}")
        print("Note: CoinGecko API has rate limits for free tier usage")


if __name__ == "__main__":
    main()
