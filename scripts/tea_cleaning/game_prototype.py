import pandas as pd
import random
from pathlib import Path

# GAME IDEA: guess the country game
# The user will enter a guess and the games picks a random country from the data
# If the country is wrong, the game compares the same indicator for the target country and the wrong country
# For example: imagine the only indicator is population density. The target country is Monaco and the user guesses Russia
# The game will return that the target country has a higher density, so the user is guided to the right answer
# Then the user will try with another country until they find the right one (we can add max tries later)

# for now I just import a subset of geo_merged (2023) to get the game logic
# NOT THE FINAL DATA!
project_root = Path(__file__).resolve().parents[2]
data_path = project_root / "data" / "clean_data_tea" / "geo_merged.csv"
df = pd.read_csv(data_path, keep_default_na=False)

# covert values to numeric and empty values as missing
df["forest_ratio"] = pd.to_numeric(df["forest_ratio"], errors="coerce")
df["pop_density"] = pd.to_numeric(df["pop_density"], errors="coerce")
# print(df["forest_ratio"].dtype)
# print(df["pop_density"].dtype)

# add area and coordinates
df["area_sq_km"] = pd.to_numeric(df["area_sq_km"], errors="coerce")
df["capital_longitude"] = pd.to_numeric(df["capital_longitude"], errors="coerce")
df["capital_latitude"] = pd.to_numeric(df["capital_latitude"], errors="coerce")
# print(df["area_sq_km"].dtype)
# print(df["capital_longitude"].dtype)
# print(df["capital_latitude"].dtype)


# take year 2023
game_data = df[df["year"] == 2023].copy()
# capital coordinates are missing for Plestine and Israel -> drop for the game
game_data.dropna(inplace=True)

# Only keep some columns for now (keep it as simple as possible) + check missing values
# -> country, continent, pop_density, forest_ratio
game_data = game_data[["country", "continent", "pop_density", "forest_ratio", "area_sq_km", "capital_longitude", "capital_latitude"]]
# print(game_data.isna().sum())
# print(game_data.info())

# pick a random target from the data -> one random country and turn it into a series/column (iloc)
# this will be hidden for the user ofc
target = game_data.sample(1).iloc[0]
#print("Target country:", target["country"])

# add a loop so the game keeps repeating until the country is guessed
guessed_correctly = False

# add attempts
attempts = 0

while not guessed_correctly:

 # ask the user to guess a country
 user_guess = input("Guess a country: ").strip()

 # find the corrisponding country in the data and make it case insensitive
 guess = game_data[game_data["country"].str.lower() == user_guess.lower()]

 # check if the user enters a valid country
 # if the country is valid it turns it into a series (match target)
 if guess.empty:
     print("Country not found")
     continue
 else:
     guess = guess.iloc[0]
     print(guess)
     attempts += 1

 # Now the "structure" of guess and target is the same and we can compare the two

 # compare continent
 if guess["continent"] == target["continent"]:
     print("continent: correct")
 else:
     print("continent: wrong")

 # compare population density -> 10% tolerance
 # 10% tolerance because is less frustrating for the user and is more inforamative 
 difference = abs(guess["pop_density"] - target["pop_density"]) # take absolute value of the difference
 tolerance = target["pop_density"] * 0.10 # 10% of the target value

 if difference <= tolerance:
     print("population density: correct")
 elif guess["pop_density"] < target["pop_density"]:
     print("population density: higher")
 else:
     print("population density: lower")

 # Compare forest coverage -> tolareance of 3 percentage points (for now)
 difference = abs(guess["forest_ratio"] - target["forest_ratio"]) # take absolute value of the difference
 tolerance = 3 # 3 percentage points tolerance

 if difference <= tolerance:
     print("forest coverage: correct")
 elif guess ["forest_ratio"] < target["forest_ratio"]:
     print("forest coverage: higher")
 else:
     print("forest coverage: lower")

 # Compare area (in square kilometers) -> 10% tolerance
 difference = abs(guess["area_sq_km"] - target["area_sq_km"])
 tolerance = target["area_sq_km"] * 0.10

 if difference <= tolerance:
     print("area: correct")
 elif guess["area_sq_km"] < target["area_sq_km"]:
     print("area: higher")
 else:
     print("area: lower")

 # compare latitude 
 if target["capital_latitude"] > guess["capital_latitude"]:
     vertical = "north"
 elif target["capital_latitude"] < guess["capital_latitude"]:
     vertical = "south"
 else:
     vertical = ""

 # compare longitude
 if target["capital_longitude"] > guess["capital_longitude"]:
     horizontal = "east"
 elif target["capital_longitude"] < guess["capital_longitude"]:
     horizontal = "west"
 else:
     horizontal = ""

 # combine directions togheter
 if vertical and horizontal:
     direction = f"{vertical}-{horizontal}"
 elif vertical:
     direction = vertical
 elif horizontal:
     direction = horizontal
 else:
     direction = "correct"

 print("direction:", direction)

 # win condition -> if the user guesses correctly, the variable becomes True and the loop stops
 if guess["country"] == target["country"]:
     print(f"you win in {attempts} guesses!")
     guessed_correctly = True
 else:
     print("try again")