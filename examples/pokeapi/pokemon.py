from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, HttpUrl

from rapid_api_client import Path, Query, RapidApi, get, rapid_default


class PokemonSprites(BaseModel):
    front_default: HttpUrl
    front_shiny: Optional[HttpUrl] = None
    back_default: Optional[HttpUrl] = None
    back_shiny: Optional[HttpUrl] = None


class PokemonType(BaseModel):
    slot: int
    type: Dict[str, str]


class PokemonAbility(BaseModel):
    ability: Dict[str, str]
    is_hidden: bool
    slot: int


class Pokemon(BaseModel):
    id: int
    name: str
    height: int
    weight: int
    sprites: PokemonSprites
    types: List[PokemonType]
    abilities: List[PokemonAbility]


class PokemonListItem(BaseModel):
    name: str
    url: HttpUrl


class PokemonList(BaseModel):
    count: int
    next: Optional[HttpUrl] = None
    previous: Optional[HttpUrl] = None
    results: List[PokemonListItem]


@rapid_default(base_url="https://pokeapi.co/api/v2")
class PokeApi(RapidApi):
    @get("/pokemon/{pokemon_id}")
    def get_pokemon(
        self,
        pokemon_id: Annotated[str, Path()],  # Can be name or ID
    ) -> Pokemon: ...

    @get("/pokemon")
    def list_pokemon(
        self,
        limit: Annotated[int, Query()] = 20,
        offset: Annotated[int, Query()] = 0,
    ) -> PokemonList: ...


def main():
    # Initialize the API client
    api = PokeApi()

    # Get a specific Pokemon by ID
    pokemon = api.get_pokemon("pikachu")
    print(f"Pokemon: {pokemon.name} (ID: {pokemon.id})")
    print(f"Height: {pokemon.height}, Weight: {pokemon.weight}")
    print(f"Types: {', '.join([t.type['name'] for t in pokemon.types])}")
    print(f"Abilities: {', '.join([a.ability['name'] for a in pokemon.abilities])}")
    print(f"Image URL: {pokemon.sprites.front_default}")

    print("\nListing Pokemon:")
    # List Pokemon with pagination
    pokemon_list = api.list_pokemon(limit=5)
    print(f"Total Pokemon count: {pokemon_list.count}")
    for item in pokemon_list.results:
        print(f"- {item.name}")


if __name__ == "__main__":
    main()
