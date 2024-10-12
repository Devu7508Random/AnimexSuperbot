import os
import json
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Initialize Bot
app = Client("anime_music_bot", 
             api_id=os.getenv('API_ID'), 
             api_hash=os.getenv('API_HASH'), 
             bot_token="7896896164:AAHDX7BIeA764CYcOTSBKpPnHHDFyrJidJM")

pytgcalls = PyTgCalls(app)
scheduler = AsyncIOScheduler()

# Owner and assistant information
OWNER_ID = 7347112176
OWNER_USERNAME = "@LYXNU7"
ASSISTANT_ID = 6966159395
ASSISTANT_USERNAME = "@Xsusnet"
CHAT_ID = -1001549596584

# Queue to store the songs
queue = []  
current_volume = 50  # Default volume
profiles = {}  # User profiles

# Load user profiles from a JSON file
def load_profiles():
    global profiles
    try:
        with open("user_profiles.json", "r") as f:
            profiles = json.load(f)
    except FileNotFoundError:
        profiles = {}

# Save user profiles to a JSON file
def save_profiles():
    with open("user_profiles.json", "w") as f:
        json.dump(profiles, f)

load_profiles()

# Command: /play
@app.on_message(filters.command('play'))
async def play_music(client, message):
    await message.reply("Playing your anime song!")
    song_name = message.text.split(maxsplit=1)[1]
    queue.append(song_name)

# Command: /queue
@app.on_message(filters.command('queue'))
async def show_queue(client, message):
    if queue:
        queue_list = "\n".join([f"{i+1}. {song}" for i, song in enumerate(queue)])
        await message.reply(f"Current Queue:\n{queue_list}")
    else:
        await message.reply("The queue is empty.")

# Command: /skip
@app.on_message(filters.command('skip'))
async def skip_song(client, message):
    if queue:
        skipped_song = queue.pop(0)
        await message.reply(f"Skipped: {skipped_song}")
        if queue:
            await message.reply(f"Now playing: {queue[0]}")
        else:
            await message.reply("The queue is now empty.")
    else:
        await message.reply("No songs in the queue to skip.")

# Fetch Lyrics (using external API)
async def fetch_lyrics(song_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.lyrics.ovh/v1/artist/{song_name}") as response:
            data = await response.json()
            return data.get('lyrics', 'Lyrics not found.')

# Command: /lyrics
@app.on_message(filters.command('lyrics'))
async def lyrics(client, message):
    if queue:
        current_song = queue[0]
        lyrics = await fetch_lyrics(current_song)
        await message.reply(f"Lyrics for {current_song}:\n{lyrics}")
    else:
        await message.reply("No song is currently playing.")

# Fetch Anime Quote (using animechan API)
async def get_anime_quote():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://animechan.xyz/api/random") as response:
            quote_data = await response.json()
            return f'"{quote_data["quote"]}" - {quote_data["character"]} ({quote_data["anime"]})'

# Command: /animequote
@app.on_message(filters.command('animequote'))
async def anime_quote(client, message):
    quote = await get_anime_quote()
    await message.reply(quote)

# Command: /randomanime
async def get_random_anime():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.jikan.moe/v4/random/anime") as response:
            anime_data = await response.json()
            return anime_data['data']['title']

@app.on_message(filters.command('randomanime'))
async def random_anime(client, message):
    anime_title = await get_random_anime()
    await message.reply(f"Random Anime Suggestion: {anime_title}")

# Command: /animeinfo
async def get_anime_info(anime_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/anime?q={anime_name}&sfw") as response:
            anime_info = await response.json()
            return anime_info['data'][0] if anime_info['data'] else None

@app.on_message(filters.command('animeinfo'))
async def anime_info(client, message):
    if len(message.command) > 1:
        anime_name = " ".join(message.command[1:])
        info = await get_anime_info(anime_name)
        if info:
            title = info['title']
            synopsis = info['synopsis']
            await message.reply(f"**{title}**\n\n{synopsis}")
        else:
            await message.reply("Anime not found.")
    else:
        await message.reply("Usage: /animeinfo [anime_name]")

# Command: /topanime
async def get_top_anime():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.jikan.moe/v4/anime?order_by=rating&sort=desc") as response:
            top_anime = await response.json()
            return [f"{anime['title']} (Rating: {anime['rating']})" for anime in top_anime['data'][:5]]

@app.on_message(filters.command('topanime'))
async def top_anime(client, message):
    top_anime_list = await get_top_anime()
    await message.reply("Top Rated Anime:\n" + "\n".join(top_anime_list))

# Command: /mangaquote
async def get_manga_quote():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.mangaquotes.com/random") as response:
            quote_data = await response.json()
            return f'"{quote_data["quote"]}" - {quote_data["author"]}'

@app.on_message(filters.command('mangaquote'))
async def manga_quote(client, message):
    quote = await get_manga_quote()
    await message.reply(quote)

# Command: /animechar
async def get_anime_character_info(character_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.jikan.moe/v4/characters?q={character_name}") as response:
            character_info = await response.json()
            return character_info['data'][0] if character_info['data'] else None

@app.on_message(filters.command('animechar'))
async def anime_char(client, message):
    if len(message.command) > 1:
        character_name = " ".join(message.command[1:])
        info = await get_anime_character_info(character_name)
        if info:
            name = info['name']
            about = info['about']
            await message.reply(f"**{name}**\n\n{about}")
        else:
            await message.reply("Character not found.")
    else:
        await message.reply("Usage: /animechar [character_name]")

# Command: /setfavoriteanime
@app.on_message(filters.command('setfavoriteanime'))
async def set_favorite_anime(client, message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        await message.reply("Usage: /setfavoriteanime [anime_name]")
        return
    favorite_anime = " ".join(message.command[1:])
    profiles[str(user_id)] = {"favorite_anime": favorite_anime}
    save_profiles()
    await message.reply(f"Your favorite anime has been set to: {favorite_anime}")

# Command: /getfavoriteanime
@app.on_message(filters.command('getfavoriteanime'))
async def get_favorite_anime(client, message):
    user_id = message.from_user.id
    favorite_anime = profiles.get(str(user_id), {}).get("favorite_anime", "not set")
    await message.reply(f"Your favorite anime is: {favorite_anime}")

# Command: /volume
@app.on_message(filters.command('volume'))
async def set_volume(client, message):
    global current_volume
    try:
        volume_level = int(message.command[1])
        if 0 <= volume_level <= 100:
            current_volume = volume_level
            await message.reply(f"Volume set to {current_volume}%")
        else:
            await message.reply("Please set a volume between 0 and 100.")
    except (IndexError, ValueError):
        await message.reply("Usage: /volume [level]")

# Fetch Anime Poll
@app.on_message(filters.command('poll'))
async def create_poll(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /poll [question]")
        return
    question = " ".join(message.command[1:])
    await message.reply(f"Poll created: {question}")

# Trivia Game (Example)
@app.on_message(filters.command('trivia'))
async def trivia_game(client, message):
    questions = {
        "What is the main character in Naruto?": "Naruto Uzumaki",
        "In which anime does Goku appear?": "Dragon Ball",
        "What is the name of the anime where humans fight Titans?": "Attack on Titan"
      }
