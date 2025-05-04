import nextcord
from nextcord.ext import commands, tasks
import aiohttp
import json
import asyncio
import os
import colorama
from colorama import Fore, Style
from datetime import datetime, timezone
from nextcord import Interaction, SlashOption, ButtonStyle, SelectOption
import asyncio
import sys
from dotenv import load_dotenv
from collections import defaultdict
import time
import random
import nextcord
from nextcord.ext import commands, tasks
import json
import os
import random
import asyncio
import time
import json
import os
from nextcord.ui import Button, View
import nextcord
from nextcord.ext import commands
from nextcord import Interaction, Embed, Button, ButtonStyle, ui
import aiohttp
import nextcord
from nextcord import Interaction, Embed, Button, ButtonStyle, ui, SlashOption
from nextcord.ext import commands  # Importamos commands
import aiohttp
import asyncio
from collections import deque
import yt_dlp

#by dearygt

def initialize_user(economy, user_id):
    default_user = {
        "berries": 0,
        "last_daily": 0,
        "bank": 0,
        "races_owned": [],
        "active_race": None,
        "inventory": [],
        "boosts": {},
        "fruits": [],
        "haki": {"observation": {"level": 0, "exp": 0}, "armament": {"level": 0, "exp": 0}, "active_buff": None},
        "achievements": {
            "bosses_killed": 0,
            "steals_succeeded": 0,
            "daily_streak": 0,
            "berries_earned": 0,
            "pirates_killed": 0,
            "marines_killed": 0,
            "seabeasts_killed": 0,
            "bandits_killed": 0,
            "islands_explored": 0,
            "trades_completed": 0,
            "bounties_hunted": 0,
            "fish_caught": 0,
            "raids_completed": 0,
            "treasures_found": 0,
            "ships_sunk": 0,
            "riddles_solved": 0,
            "arenas_won": 0,
            "crews_joined": 0,
            "shipwrecks_salvaged": 0,
            "markets_traded": 0,
            "krakens_faced": 0
        }
    }
    if user_id not in economy:
        economy[user_id] = default_user.copy()
    for key, value in default_user.items():
        if key not in economy[user_id]:
            economy[user_id][key] = value
        if key == "achievements":
            for ach, val in default_user["achievements"].items():
                if ach not in economy[user_id]["achievements"]:
                    economy[user_id]["achievements"][ach] = val
    return economy

def load_boss_config():
    if os.path.exists("boss_config.json"):
        with open("boss_config.json", "r") as f:
            return json.load(f)
    return {}

def save_boss_config(data):
    with open("boss_config.json", "w") as f:
        json.dump(data, f, indent=4)

# Initialize colorama
colorama.init()
def print_log(message, color=Fore.WHITE):
    print(f"{Fore.CYAN}[{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}] {color}{message}{Style.RESET_ALL}")

# Loading animation
async def loading_menu():
    print_log("Starting Blox Fruits Bot...", Fore.YELLOW)
    for i in range(3):
        sys.stdout.write(f"\r{Fore.GREEN}Loading{'.' * (i+1)}")
        sys.stdout.flush()
        await asyncio.sleep(0.5)
    sys.stdout.write("\r")
    print_log("Bot Loaded Successfully!", Fore.GREEN)

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = [int(id) for id in os.getenv("OWNER_IDS").split(",")] if os.getenv("OWNER_IDS") else []
SUPPORT_SERVER = os.getenv("SUPPORT_SERVER", "https://discord.gg/invite")
BOT_INVITE = os.getenv("BOT_INVITE", "https://discord.com/oauth2/authorize")
FEEDBACK_CHANNEL_ID = int(os.getenv("FEEDBACK_CHANNEL_ID")) if os.getenv("FEEDBACK_CHANNEL_ID") else None

# Bot setup
intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="?", intents=intents)

IMAGE_API_KEY = "KEY"
IMAGE_API_URL = "https://test-hub.kys.gay/api/image"

AUDIO_API_KEY = "your_api_key"
AUDIO_API_URL = "https://test-hub.kys.gay/api/audio/mp3"

API_URL = "http://test-hub.kys.gay/api/stock/bloxfruit"

# Rate limiting
last_api_call = 0
API_COOLDOWN = 5
API_TIMEOUT = 10
API_RETRIES = 3

# Expanded fruit data with images
FRUITS = [
    {"name": "Flame", "rarity": "Common", "chance": 0.25, "image": "https://example.com/flame.png"},
    {"name": "Ice", "rarity": "Common", "chance": 0.25, "image": "https://example.com/ice.png"},
    {"name": "Sand", "rarity": "Common", "chance": 0.20, "image": "https://example.com/sand.png"},
    {"name": "Magma", "rarity": "Rare", "chance": 0.10, "image": "https://example.com/magma.png"},
    {"name": "Dark", "rarity": "Rare", "chance": 0.10, "image": "https://example.com/dark.png"},
    {"name": "Light", "rarity": "Rare", "chance": 0.05, "image": "https://example.com/light.png"},
    {"name": "Dragon", "rarity": "Legendary", "chance": 0.03, "image": "https://example.com/dragon.png"},
    {"name": "Kitsune", "rarity": "Mythical", "chance": 0.01, "image": "https://example.com/kitsune.png"},
    {"name": "Buddha", "rarity": "Legendary", "chance": 0.03, "image": "https://example.com/buddha.png"},
    {"name": "Leopard", "rarity": "Mythical", "chance": 0.01, "image": "https://example.com/leopard.png"},
    {"name": "Venom", "rarity": "Mythical", "chance": 0.01, "image": "https://example.com/venom.png"},
    {"name": "Dough", "rarity": "Mythical", "chance": 0.01, "image": "https://example.com/dough.png"}
]

# Shop items
SHOP_ITEMS = {
    "reroll_token": {"name": "Reroll Token", "price": 50, "description": "Grants one fruit reroll"},
    "rare_fruit": {"name": "Rare Fruit", "price": 200, "description": "Guarantees a Rare or better fruit"}
}

# Load config
def load_config():
    default_guild_config = {
        "stock_channel_ids": [],
        "mirage_role_id": None,
        "normal_role_id": None,
        "log_channel_id": None,
        "auto_check_interval": 5400,
        "auto_update_enabled": True,
        "embed_color": 0xFF0000,
        "first_setup": True,
        "last_update": 0,
        "private_commands": []
    }
    config_data = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config_data = json.load(f)
    return config_data, default_guild_config

def load_economy():
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)

def save_config(config_data, force=False):
    if not force:
        with open("config.json", "r") as f:
            old_data = json.load(f)
        if old_data == config_data:
            return
    with open("config.json", "w") as f:
        json.dump(config_data, f, indent=4)

config_data, default_guild_config = load_config()

def get_guild_config(guild_id):
    guild_id_str = str(guild_id)
    if guild_id_str not in config_data:
        config_data[guild_id_str] = default_guild_config.copy()
        save_config(config_data)
    return config_data[guild_id_str]

# Load stock cache
def load_cache():
    if os.path.exists("stock_cache.json"):
        with open("stock_cache.json", "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open("stock_cache.json", "w") as f:
        json.dump(cache, f, indent=4)

# Load inventory data
def load_inventory():
    if os.path.exists("inventory.json"):
        with open("inventory.json", "r") as f:
            return json.load(f)
    return {}

def save_inventory(data):
    with open("inventory.json", "w") as f:
        json.dump(data, f, indent=4)

# Load economy data
def load_economy():
    if os.path.exists("economy.json"):
        with open("economy.json", "r") as f:
            return json.load(f)
    return {}

def save_economy(data):
    with open("economy.json", "w") as f:
        json.dump(data, f, indent=4)

# Load stock history
def load_stock_history():
    if os.path.exists("stock_history.json"):
        with open("stock_history.json", "r") as f:
            return json.load(f)
    return []

def save_stock_history(history):
    with open("stock_history.json", "w") as f:
        json.dump(history, f, indent=4)

# Tutorial embed
def create_tutorial_embed(channel, guild_config):
    embed = nextcord.Embed(
        title="🎉 Stock Channel Added!",
        description=(
            f"**{channel.mention}** is now set to receive automatic stock updates!\n"
            "The bot will send **Normal Stock** and **Mirage Stock** embeds whenever there are changes, "
            f"every {guild_config['auto_check_interval']//60} minutes (if enabled).\n\n"
            "**Next Steps**:\n"
            "- **Set Ping Roles**: Use `/setrole` to notify users for stock changes.\n"
            "- **Check Settings**: Run `/settings` to verify configurations.\n"
            "- **Trade Fruits**: Try `?tradefruit` to trade with others!\n"
            "- **Earn Berries**: Use `?daily` to collect Berries.\n"
            "- **View Stock**: Use `/stock` to see current stock.\n"
            "Run `/help` for all commands or `?help` for economy commands!"
        ),
        color=guild_config["embed_color"]
    )
    embed.set_footer(text="Blox Fruits Bot")
    return embed

# Setup View
class SetupView(nextcord.ui.View):
    def __init__(self, guild_id):
        super().__init__(timeout=None)
        self.guild_id = guild_id

    @nextcord.ui.select(
        placeholder="Select an option...",
        options=[
            SelectOption(label="Add Stock Channel", value="stock_channel", emoji="📊"),
            SelectOption(label="Remove Stock Channel", value="remove_stock_channel", emoji="🗑️"),
            SelectOption(label="Set Log Channel", value="log_channel", emoji="📜"),
            SelectOption(label="Create Ping Roles", value="create_roles", emoji="🔔"),
            SelectOption(label="Delete Ping Roles", value="delete_roles", emoji="🗑️"),
            SelectOption(label="Toggle Auto-Updates", value="toggle_auto", emoji="🔄"),
            SelectOption(label="Set Embed Color", value="set_color", emoji="🎨"),
            SelectOption(label="Clear Cache", value="clear_cache", emoji="🧹"),
            SelectOption(label="Sync Commands", value="sync_commands", emoji="🔄")
        ]
    )
    async def setup_select(self, select: nextcord.ui.Select, interaction: Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
            return

        guild_config = get_guild_config(self.guild_id)
        value = select.values[0]

        if value == "stock_channel":
            await interaction.response.send_message("Please mention the channel to add for stock updates:", ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.channel_mentions
            try:
                msg = await bot.wait_for("message", check=check, timeout=30)
                channel = msg.channel_comments[0]
                if channel.id not in guild_config["stock_channel_ids"]:
                    guild_config["stock_channel_ids"].append(channel.id)
                    save_config(config_data)
                    await interaction.followup.send(f"✅ Added {channel.mention} to stock channels", ephemeral=True)
                    await interaction.followup.send(embed=create_tutorial_embed(channel, guild_config), ephemeral=True)

                    if guild_config["first_setup"]:
                        await interaction.followup.send("Fetching initial stock...", ephemeral=True)
                        data = await fetch_stock()
                        if data:
                            normal_stock = data.get("normal_stock", {}).get("items", [])
                            mirage_stock = data.get("mirage_stock", {}).get("items", [])
                            await channel.send(embed=create_stock_embed(normal_stock, "Initial Normal Stock"))
                            await channel.send(embed=create_stock_embed(mirage_stock, "Initial Mirage Stock"))
                            guild_config["first_setup"] = False
                            save_config(config_data)
                        else:
                            await interaction.followup.send("⚠️ Failed to fetch initial stock!", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ {channel.mention} is already a stock channel!", ephemeral=True)
            except:
                await interaction.followup.send("❌ No valid channel provided or timed out!", ephemeral=True)

        elif value == "remove_stock_channel":
            if not guild_config["stock_channel_ids"]:
                await interaction.response.send_message("❌ No stock channels set!", ephemeral=True)
                return
            options = [SelectOption(label=str(bot.get_channel(cid).name), value=str(cid)) for cid in guild_config["stock_channel_ids"] if bot.get_channel(cid)]
            select_menu = nextcord.ui.Select(placeholder="Select channel to remove...", options=options)
            async def remove_callback(inter: Interaction):
                cid = int(select_menu.values[0])
                guild_config["stock_channel_ids"].remove(cid)
                save_config(config_data)
                await inter.response.send_message(f"✅ Removed <#{cid}> from stock channels", ephemeral=True)
            select_menu.callback = remove_callback
            view = nextcord.ui.View()
            view.add_item(select_menu)
            await interaction.response.send_message("Select a channel to remove:", view=view, ephemeral=True)

        elif value == "log_channel":
            await interaction.response.send_message("Please mention the channel for logs:", ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.channel_mentions
            try:
                msg = await bot.wait_for("message", check=check, timeout=30)
                channel = msg.channel_mentions[0]
                guild_config["log_channel_id"] = channel.id
                save_config(config_data)
                await interaction.followup.send(f"✅ Log channel set to {channel.mention}", ephemeral=True)
            except:
                await interaction.followup.send("❌ No valid channel provided or timed out!", ephemeral=True)

        elif value == "create_roles":
            await interaction.response.defer()
            normal_role = await interaction.guild.create_role(name="Normal Stock Ping", mentionable=True)
            mirage_role = await interaction.guild.create_role(name="Mirage Stock Ping", mentionable=True)
            guild_config["normal_role_id"] = normal_role.id
            guild_config["mirage_role_id"] = mirage_role.id
            save_config(config_data)
            await interaction.followup.send(f"✅ Created roles: {normal_role.mention}, {mirage_role.mention}", ephemeral=True)

        elif value == "delete_roles":
            await interaction.response.defer()
            for role_id in [guild_config["normal_role_id"], guild_config["mirage_role_id"]]:
                if role_id:
                    role = interaction.guild.get_role(role_id)
                    if role:
                        await role.delete()
            guild_config["normal_role_id"] = None
            guild_config["mirage_role_id"] = None
            save_config(config_data)
            await interaction.followup.send("✅ Deleted ping roles", ephemeral=True)

        elif value == "toggle_auto":
            guild_config["auto_update_enabled"] = not guild_config["auto_update_enabled"]
            save_config(config_data)
            await interaction.response.send_message(f"✅ Auto-updates {'enabled' if guild_config['auto_update_enabled'] else 'disabled'}", ephemeral=True)

        elif value == "set_color":
            await interaction.response.send_message("Enter hex color code (e.g., FF0000):", ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await bot.wait_for("message", check=check, timeout=30)
                color = int(msg.content.strip("#"), 16)
                guild_config["embed_color"] = color
                save_config(config_data)
                await interaction.followup.send(f"✅ Embed color set to #{color:06x}", ephemeral=True)
            except:
                await interaction.followup.send("❌ Invalid color or timeout", ephemeral=True)

        elif value == "clear_cache":
            save_cache({})
            await interaction.response.send_message("✅ Stock cache cleared", ephemeral=True)

        elif value == "sync_commands":
            await bot.sync_all_application_commands()
            print_log("Slash commands synced globally", Fore.GREEN)
            await interaction.response.send_message("✅ Slash commands synced globally", ephemeral=True)

# Settings View
class SettingsView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(nextcord.ui.Button(
            label="Support Server",
            style=ButtonStyle.url,
            url=SUPPORT_SERVER,
            emoji="📩"
        ))
        self.add_item(nextcord.ui.Button(
            label="Invite Bot",
            style=ButtonStyle.url,
            url=BOT_INVITE,
            emoji="🤖"
        ))

# Welcome View
class WelcomeView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(nextcord.ui.Button(
            label="Support Server",
            style=ButtonStyle.url,
            url=SUPPORT_SERVER,
            emoji="📩"
        ))
        self.add_item(nextcord.ui.Button(
            label="Invite Bot",
            style=ButtonStyle.url,
            url=BOT_INVITE,
            emoji="🤖"
        ))

# Stock View
class StockView(nextcord.ui.View):
    def __init__(self, normal_stock, mirage_stock):
        super().__init__(timeout=None)
        self.normal_stock = normal_stock
        self.mirage_stock = mirage_stock

    @nextcord.ui.button(label="View Normal", style=ButtonStyle.red, emoji="🍎")
    async def normal_button(self, button: nextcord.ui.Button, interaction: Interaction):
        embed = create_stock_embed(self.normal_stock, "Normal Stock")
        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="View Mirage", style=ButtonStyle.red, emoji="<:mirage:1362041169999036426>")
    async def mirage_button(self, button: nextcord.ui.Button, interaction: Interaction):
        embed = create_stock_embed(self.mirage_stock, "Mirage Stock")
        await interaction.response.edit_message(embed=embed, view=self)

    @nextcord.ui.button(label="Refresh", style=ButtonStyle.green, emoji="<:refresh:1362041599869190307>")
    async def refresh_button(self, button: nextcord.ui.Button, interaction: Interaction):
        global last_api_call
        if time.time() - last_api_call < API_COOLDOWN:
            await interaction.response.send_message("⏳ Please wait before refreshing!", ephemeral=True)
            return
        await interaction.response.defer()
        data = await fetch_stock()
        if data:
            self.normal_stock = data.get("normal_stock", {}).get("items", [])
            self.mirage_stock = data.get("mirage_stock", {}).get("items", [])
            embed = create_stock_embed(self.normal_stock, "Normal Stock")
            await interaction.followup.send(embed=embed, view=self)
        else:
            await interaction.followup.send("❌ Failed to refresh stock!", ephemeral=True)

# Trade View
class TradeView(nextcord.ui.View):
    def __init__(self, initiator, target, initiator_fruit, target_fruit):
        super().__init__(timeout=60)
        self.initiator = initiator
        self.target = target
        self.initiator_fruit = initiator_fruit
        self.target_fruit = target_fruit

    @nextcord.ui.button(label="Accept", style=ButtonStyle.green, emoji="✅")
    async def accept_button(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ Only the trade target can accept!", ephemeral=True)
            return
        inventory = load_inventory()
        economy = load_economy()
        initiator_id = str(self.initiator.id)
        target_id = str(self.target.id)

        if initiator_id not in inventory or self.initiator_fruit not in inventory[initiator_id]:
            await interaction.response.send_message("❌ Initiator no longer has the fruit!", ephemeral=True)
            return
        if target_id not in inventory or self.target_fruit not in inventory[target_id]:
            await interaction.response.send_message("❌ You no longer have the fruit!", ephemeral=True)
            return

        # Swap fruits
        inventory[initiator_id].remove(self.initiator_fruit)
        inventory[target_id].remove(self.target_fruit)
        inventory[initiator_id].append(self.target_fruit)
        inventory[target_id].append(self.initiator_fruit)
        save_inventory(inventory)

        # Reward 10 Berries to both for trading
        economy[initiator_id]["berries"] = economy.get(initiator_id, {"berries": 0, "last_daily": 0})["berries"] + 10
        economy[target_id]["berries"] = economy.get(target_id, {"berries": 0, "last_daily": 0})["berries"] + 10
        save_economy(economy)

        await interaction.response.send_message(f"✅ Trade successful! {self.initiator.mention} and {self.target.mention} swapped fruits and earned 10 Berries each!", ephemeral=False)
        self.stop()

    @nextcord.ui.button(label="Decline", style=ButtonStyle.red, emoji="❌")
    async def decline_button(self, button: nextcord.ui.Button, interaction: Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("❌ Only the trade target can decline!", ephemeral=True)
            return
        await interaction.response.send_message(f"❌ Trade declined by {self.target.mention}.", ephemeral=False)
        self.stop()

# Owner Menu
class OwnerMenu(nextcord.ui.Select):
    def __init__(self):
        options = [
            SelectOption(label="List Servers", value="servers", emoji="🌐"),
            SelectOption(label="List Channels", value="channels", emoji="📜"),
            SelectOption(label="Test Ping", value="testping", emoji="🔔"),
            SelectOption(label="Restart Auto-Update", value="restart", emoji="🔄"),
            SelectOption(label="Clear Cache", value="clearcache", emoji="🧹"),
            SelectOption(label="Sync Commands", value="sync", emoji="🔄"),
            SelectOption(label="Change Embed Color", value="color", emoji="🎨"),
            SelectOption(label="Shutdown", value="shutdown", emoji="🛑")
        ]
        super().__init__(placeholder="Select an action...", options=options)

    async def callback(self, interaction: Interaction):
        if interaction.user.id not in OWNER_IDS:
            await interaction.response.send_message("❌ Unauthorized!", ephemeral=True)
            return

        guild_config = get_guild_config(interaction.guild_id)
        if self.values[0] == "servers":
            embed = nextcord.Embed(title="🌐 Servers", color=guild_config["embed_color"])
            for guild in bot.guilds:
                embed.add_field(name=guild.name, value=f"ID: {guild.id} | Members: {guild.member_count}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.values[0] == "channels":
            embed = nextcord.Embed(title="📜 Channels", color=guild_config["embed_color"])
            for channel in interaction.guild.text_channels:
                embed.add_field(name=channel.name, value=f"ID: {channel.id}", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif self.values[0] == "testping":
            mirage_role = interaction.guild.get_role(guild_config["mirage_role_id"])
            normal_role = interaction.guild.get_role(guild_config["normal_role_id"])
            content = f"Mirage: {mirage_role.mention if mirage_role else 'Not set'}\nNormal: {normal_role.mention if normal_role else 'Not set'}"
            await interaction.response.send_message(content, ephemeral=False)

        elif self.values[0] == "restart":
            auto_stock_update.restart()
            await interaction.response.send_message("✅ Auto-update task restarted", ephemeral=True)

        elif self.values[0] == "clearcache":
            save_cache({})
            await interaction.response.send_message("✅ Stock cache cleared", ephemeral=True)

        elif self.values[0] == "sync":
            await bot.sync_all_application_commands()
            print_log("Slash commands synced globally", Fore.GREEN)
            await interaction.response.send_message("✅ Slash commands synced globally", ephemeral=True)

        elif self.values[0] == "color":
            await interaction.response.send_message("Enter hex color code (e.g., FF0000):", ephemeral=True)
            def check(m):
                return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
            try:
                msg = await bot.wait_for("message", check=check, timeout=30)
                color = int(msg.content.strip("#"), 16)
                guild_config["embed_color"] = color
                save_config(config_data)
                await interaction.followup.send(f"✅ Embed color set to #{color:06x}", ephemeral=True)
            except:
                await interaction.followup.send("❌ Invalid color or timeout", ephemeral=True)

        elif self.values[0] == "shutdown":
            await interaction.response.send_message("🛑 Shutting down...", ephemeral=True)
            print_log("Bot shutting down...", Fore.RED)
            await bot.close()

class OwnerView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(OwnerMenu())

# Stock embed
def create_stock_embed(stock, title):
    embed = nextcord.Embed(title=f"🍎 {title}", color=default_guild_config["embed_color"], timestamp=datetime.now(timezone.utc))
    embed.set_footer(text="Blox Fruits Bot")
    if not stock:
        embed.description = "No items in stock."
        return embed
    for item in stock:
        if isinstance(item, str):
            name = item
            robux = "N/A"
            usd = "N/A"
        else:
            name = item.get("name", "Unknown")
            robux = item.get("robux_price", "N/A")
            usd = item.get("usd_price", "N/A")
        embed.add_field(
            name=f"**{name}**",
            value=f"<:Robux:1362033722026889397> Robux: {robux}\n<:Money:1362032925838934048> USD: {usd}",
            inline=True
        )
        if not isinstance(item, str) and (image_url := item.get("image_url")):
            embed.set_thumbnail(url=image_url)
    return embed

# Detailed stock embed
def create_detailed_stock_embed(normal_stock, mirage_stock, changes=None, embed_color=0xFF0000):
    embed = nextcord.Embed(title="📊 Detailed Blox Fruits Stock", color=embed_color, timestamp=datetime.now(timezone.utc))
    embed.set_footer(text="Blox Fruits Bot")

    normal_text = ""
    for item in normal_stock or []:
        if isinstance(item, str):
            normal_text += f"**{item}**\n<:Robux:1362033722026889397> Robux: N/A\n/add type:emoji id:98790-money USD: N/A\n\n"
        else:
            name = item.get("name", "Unknown")
            robux = item.get("robux_price", "N/A")
            usd = item.get("usd_price", "N/A")
            normal_text += f"**{name}**\n<:Robux:1362033722026889397> Robux: {robux}\n<:Money:1362032925838934048> USD: {usd}\n\n"
    embed.add_field(name="🍎 Normal Stock", value=normal_text or "No items", inline=False)

    mirage_text = ""
    for item in mirage_stock or []:
        if isinstance(item, str):
            mirage_text += f"**{item}**\n<:Robux:1362033722026889397> Robux: N/A\n<:Money:1362032925838934048> USD: N/A\n\n"
        else:
            name = item.get("name", "Unknown")
            robux = item.get("robux_price", "N/A")
            usd = item.get("usd_price", "N/A")
            mirage_text += f"**{name}**\n<:Robux:1362033722026889397> Robux: {robux}\n<:Money:1362032925838934048> USD: {usd}\n\n"
    embed.add_field(name="🌌 Mirage Stock", value=mirage_text or "No items", inline=False)

    if changes:
        changes_text = ""
        for stock_type, change in changes.items():
            added = change.get("added", [])
            removed = change.get("removed", [])
            if added:
                added_names = []
                for item in added:
                    if isinstance(item, str):
                        added_names.append(item)
                    else:
                        added_names.append(item.get("name", "Unknown"))
                changes_text += f"**{stock_type.capitalize()} Added**:\n" + "\n".join([f"- {name}" for name in added_names]) + "\n"
            if removed:
                removed_names = []
                for item in removed:
                    if isinstance(item, str):
                        removed_names.append(item)
                    else:
                        removed_names.append(item.get("name", "Unknown"))
                changes_text += f"**{stock_type.capitalize()} Removed**:\n" + "\n".join([f"- {name}" for name in removed_names]) + "\n"
        if changes_text:
            embed.add_field(name="🔄 Changes", value=changes_text, inline=False)

    return embed

# Log errors
async def log_error(message, guild_id=None):
    if guild_id:
        guild_config = get_guild_config(guild_id)
        if guild_config["log_channel_id"]:
            channel = bot.get_channel(guild_config["log_channel_id"])
            if channel:
                embed = nextcord.Embed(title="⚠️ Error Log", description=message[:2000], color=guild_config["embed_color"])
                await channel.send(embed=embed)
                return
    for owner_id in OWNER_IDS:
        try:
            owner = await bot.fetch_user(owner_id)
            embed = nextcord.Embed(title="⚠️ Error Log", description=message[:2000], color=0xFF0000)
            embed.add_field(name="Guild ID", value=str(guild_id) if guild_id else "N/A", inline=False)
            await owner.send(embed=embed)
        except:
            pass
    print_log(message, Fore.RED)

# Fetch stock
async def fetch_stock():
    global last_api_call
    cache = load_cache()
    cache_key = f"stock_{int(time.time() // 300)}"
    if cache_key in cache:
        return cache[cache_key]

    if time.time() - last_api_call < API_COOLDOWN:
        await asyncio.sleep(API_COOLDOWN - (time.time() - last_api_call))
    
    for attempt in range(API_RETRIES):
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)) as session:
                async with session.get(API_URL) as response:
                    last_api_call = time.time()
                    if response.status == 200:
                        data = await response.json()
                        cache[cache_key] = data
                        save_cache(cache)
                        print_log(f"API request successful: {response.status}", Fore.GREEN)
                        return data
                    else:
                        error_msg = f"API Error: Status {response.status}"
                        print_log(error_msg, Fore.RED)
                        await log_error(error_msg)
                        if attempt == API_RETRIES - 1:
                            return None
                        await asyncio.sleep(2 ** attempt)
        except Exception as e:
            error_msg = f"API Request Failed (Attempt {attempt + 1}/{API_RETRIES}): {str(e)}"
            print_log(error_msg, Fore.RED)
            await log_error(error_msg)
            if attempt == API_RETRIES - 1:
                return None
            await asyncio.sleep(2 ** attempt)
    return None

# Compare stocks
def compare_stocks(old_stock, new_stock):
    old_names = set()
    for item in old_stock:
        if isinstance(item, str):
            old_names.add(item)
        else:
            old_names.add(item.get("name", ""))
    new_names = set()
    for item in new_stock:
        if isinstance(item, str):
            new_names.add(item)
        else:
            new_names.add(item.get("name", ""))
    added = [item for item in new_stock if (isinstance(item, str) and item not in old_names) or (not isinstance(item, str) and item.get("name", "") not in old_names)]
    removed = [item for item in old_stock if (isinstance(item, str) and item not in new_names) or (not isinstance(item, str) and item.get("name", "") not in new_names)]
    return {"added": added, "removed": removed}

# Auto-update task
@tasks.loop(seconds=60)
async def auto_stock_update():
    for guild in bot.guilds:
        guild_config = get_guild_config(guild.id)
        if not guild_config["auto_update_enabled"] or not guild_config["stock_channel_ids"]:
            continue

        last_update = guild_config.get("last_update", 0)
        if time.time() - last_update < guild_config["auto_check_interval"]:
            continue

        guild_config["last_update"] = time.time()
        save_config(config_data)

        channels = [bot.get_channel(cid) for cid in guild_config["stock_channel_ids"]]
        channels = [c for c in channels if c]

        if not channels:
            await log_error("No valid stock channels found!", guild.id)
            continue

        data = await fetch_stock()
        if not data:
            continue

        cache = load_cache()
        inventory = load_inventory()
        normal_stock = data.get("normal_stock", {}).get("items", [])
        mirage_stock = data.get("mirage_stock", {}).get("items", [])

        guild_cache = cache.get(str(guild.id), {})
        normal_changes = compare_stocks(guild_cache.get("normal_stock", []), normal_stock)
        mirage_changes = compare_stocks(guild_cache.get("mirage_stock", []), mirage_stock)

        cache[str(guild.id)] = {"normal_stock": normal_stock, "mirage_stock": mirage_stock}
        save_cache(cache)

        history = load_stock_history()
        history.append({
            "guild_id": guild.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "normal_stock": normal_stock,
            "mirage_stock": mirage_stock,
            "changes": {"normal": normal_changes, "mirage": mirage_changes}
        })
        if len(history) > 50:
            history = history[-50:]
        save_stock_history(history)

        for channel in channels:
            try:
                if normal_changes["added"] or normal_changes["removed"]:
                    normal_role = guild.get_role(guild_config["normal_role_id"])
                    content = normal_role.mention if normal_role else ""
                    embed = create_stock_embed(normal_stock, "Normal Stock")
                    embed.color = guild_config["embed_color"]
                    await channel.send(content=content.strip(), embed=embed)

                if mirage_changes["added"] or mirage_changes["removed"]:
                    mirage_role = guild.get_role(guild_config["mirage_role_id"])
                    content = mirage_role.mention if mirage_role else ""
                    embed = create_stock_embed(mirage_stock, "Mirage Stock")
                    embed.color = guild_config["embed_color"]
                    await channel.send(content=content.strip(), embed=embed)
            except Exception as e:
                await log_error(f"Failed to send update to {channel.name}: {str(e)}", guild.id)

        for user_id, fruits in inventory.items():
            user = await bot.fetch_user(int(user_id))
            if not user:
                continue
            for fruit in fruits:
                for item in normal_stock + mirage_stock:
                    item_name = item if isinstance(item, str) else item.get("name", "")
                    if item_name.lower() == fruit.lower():
                        robux = "N/A" if isinstance(item, str) else item.get("robux_price", "N/A")
                        usd = "N/A" if isinstance(item, str) else item.get("usd_price", "N/A")
                        embed = nextcord.Embed(
                            title=f"🎯 Fruit Sniped!",
                            description=f"**{item_name}** is in stock!\n💰 Robux: {robux}\n💵 USD: {usd}",
                            color=guild_config["embed_color"]
                        )
                        if not isinstance(item, str) and item.get("image_url"):
                            embed.set_thumbnail(url=item["image_url"])
                        try:
                            await user.send(embed=embed)
                        except:
                            await log_error(f"Failed to DM user {user_id}", guild.id)

# Bot events
@bot.event
async def on_ready():
    print_log(f"Logged in as {bot.user}", Fore.GREEN)
    await bot.sync_all_application_commands()
    print_log("Slash commands synced globally", Fore.GREEN)
    await loading_menu()
    auto_stock_update.start()

@bot.event
async def on_guild_join(guild):
    embed = nextcord.Embed(
        title="Welcome to Blox Fruits Bot! 🎉",
        description=(
            "Thanks for inviting me! Here's how to get started:\n"
            "🔹 **/setup**: Configure the bot (Admin only).\n"
            "🔹 **/stock**: View current Blox Fruits stock.\n"
            "🔹 **?rerollfruit**: Reroll for a random fruit (50 Berries).\n"
            "🔹 **?tradefruit**: Trade fruits with others.\n"
            "🔹 **?daily**: Claim daily Berries.\n"
            "🔹 **/help**: See all commands.\n"
            "🔹 **?help**: See economy commands.\n"
            "Set up stock channels with `/setup` to receive updates every 1.5 hours!"
        ),
        color=default_guild_config["embed_color"]
    )
    embed.set_footer(text="Blox Fruits Bot")
    view = WelcomeView()
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed, view=view)
            break

# Slash commands
@bot.slash_command(description="View Blox Fruits stock")
@commands.cooldown(1, 10, commands.BucketType.user)
async def stock(interaction: Interaction, dm: bool = SlashOption(description="Send to DM?", default=False)):
    await interaction.response.defer()
    data = await fetch_stock()
    if not data:
        await interaction.followup.send("❌ Failed to fetch stock! Check logs.", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    normal_stock = data.get("normal_stock", {}).get("items", [])
    mirage_stock = data.get("mirage_stock", {}).get("items", [])
    embed = create_stock_embed(normal_stock, "Normal Stock")
    embed.color = guild_config["embed_color"]
    view = StockView(normal_stock, mirage_stock)

    if dm:
        try:
            await interaction.user.send(embed=embed, view=view)
            await interaction.followup.send("✅ Stock sent to your DMs!", ephemeral=True)
        except:
            await interaction.followup.send("❌ Failed to send DM!", ephemeral=True)
    else:
        message = await interaction.followup.send(embed=embed, view=view)
        await message.add_reaction("🇼")  # W
        await message.add_reaction("🇱")  # L

@bot.slash_command(description="View detailed Blox Fruits stock")
@commands.cooldown(1, 10, commands.BucketType.user)
async def detailedstock(interaction: Interaction):
    await interaction.response.defer()
    data = await fetch_stock()
    if not data:
        await interaction.followup.send("❌ Failed to fetch stock!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    normal_stock = data.get("normal_stock", {}).get("items", [])
    mirage_stock = data.get("mirage_stock", {}).get("items", [])
    embed = create_detailed_stock_embed(normal_stock, mirage_stock, embed_color=guild_config["embed_color"])
    await interaction.followup.send(embed=embed)

@bot.slash_command(description="Filter stock by criteria")
@commands.cooldown(1, 10, commands.BucketType.user)
async def filterstock(
    interaction: Interaction,
    stock_type: str = SlashOption(description="Stock type", choices=["normal", "mirage"], required=True),
    max_robux: int = SlashOption(description="Max Robux price", required=False, default=None),
    fruit_name: str = SlashOption(description="Fruit name (partial match)", required=False, default=None)
):
    await interaction.response.defer()
    data = await fetch_stock()
    if not data:
        await interaction.followup.send("❌ Failed to fetch stock!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    stock = data.get(f"{stock_type}_stock", {}).get("items", [])
    filtered = stock

    if max_robux:
        filtered = [
            item for item in filtered
            if not isinstance(item, str) and item.get("robux_price", "N/A") != "N/A" and
            float(item["robux_price"].replace("R$", "").replace("k", "000").replace(".", "")) <= max_robux
        ]
    if fruit_name:
        filtered = [
            item for item in filtered
            if (isinstance(item, str) and fruit_name.lower() in item.lower()) or
            (not isinstance(item, str) and fruit_name.lower() in item.get("name", "").lower())
        ]

    embed = create_stock_embed(filtered, f"Filtered {stock_type.capitalize()} Stock")
    embed.color = guild_config["embed_color"]
    await interaction.followup.send(embed=embed)

@bot.slash_command(description="Add stock update channel")
async def setchannelstock(interaction: Interaction, channel: nextcord.TextChannel = SlashOption(description="Channel for stock updates")):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    await interaction.response.defer()
    guild_config = get_guild_config(interaction.guild_id)
    if channel.id not in guild_config["stock_channel_ids"]:
        guild_config["stock_channel_ids"].append(channel.id)
        save_config(config_data)

        if guild_config["first_setup"]:
            data = await fetch_stock()
            if data:
                normal_stock = data.get("normal_stock", {}).get("items", [])
                mirage_stock = data.get("mirage_stock", {}).get("items", [])
                await channel.send(embed=create_stock_embed(normal_stock, "Initial Normal Stock"))
                await channel.send(embed=create_stock_embed(mirage_stock, "Initial Mirage Stock"))
                guild_config["first_setup"] = False
                save_config(config_data)
            else:
                await interaction.followup.send("⚠️ Stock channel added, but failed to fetch initial stock.", ephemeral=True)
                return

        await interaction.followup.send(f"✅ Added {channel.mention} to stock channels", ephemeral=True)
        await interaction.followup.send(embed=create_tutorial_embed(channel, guild_config), ephemeral=True)
    else:
        await interaction.followup.send(f"❌ {channel.mention} is already a stock channel!", ephemeral=True)

@bot.slash_command(description="Set log channel")
async def setlogchannel(interaction: Interaction, channel: nextcord.TextChannel = SlashOption(description="Channel for logs")):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    guild_config["log_channel_id"] = channel.id
    save_config(config_data)
    await interaction.response.send_message(f"✅ Log channel set to {channel.mention}", ephemeral=True)

@bot.slash_command(description="Set role for stock pings")
async def setrole(interaction: Interaction, stock_type: str = SlashOption(description="Stock type", choices=["mirage", "normal"]), role: nextcord.Role = SlashOption(description="Role to ping")):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    if stock_type == "mirage":
        guild_config["mirage_role_id"] = role.id
    else:
        guild_config["normal_role_id"] = role.id
    save_config(config_data)
    await interaction.response.send_message(f"✅ {stock_type.capitalize()} role set to {role.mention}", ephemeral=True)

@bot.slash_command(description="Manually ping stock role")
async def stockping(interaction: Interaction, stock_type: str = SlashOption(description="Stock type", choices=["mirage", "normal"])):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    role_id = guild_config["mirage_role_id"] if stock_type == "mirage" else guild_config["normal_role_id"]
    role = interaction.guild.get_role(role_id)
    if role:
        await interaction.response.send_message(f"{role.mention} {stock_type.capitalize()} stock update!")
    else:
        await interaction.response.send_message("❌ Role not set!", ephemeral=True)

@bot.slash_command(description="Show bot latency")
async def ping(interaction: Interaction):
    await interaction.response.send_message(f"🏓 Latency: {round(bot.latency * 1000)}ms")

@bot.slash_command(description="View current settings")
async def settings(interaction: Interaction):
    guild_config = get_guild_config(interaction.guild_id)
    channels = [bot.get_channel(cid) for cid in guild_config["stock_channel_ids"]]
    log_channel = bot.get_channel(guild_config["log_channel_id"])
    mirage_role = interaction.guild.get_role(guild_config["mirage_role_id"])
    normal_role = interaction.guild.get_role(guild_config["normal_role_id"])
    embed = nextcord.Embed(title="⚙️ Bot Settings", color=guild_config["embed_color"], timestamp=datetime.now(timezone.utc))
    embed.set_footer(text="Blox Fruits Bot")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.add_field(
        name="📊 Stock Channels",
        value="\n".join([c.mention for c in channels if c]) if channels else "❌ None set",
        inline=True
    )
    embed.add_field(
        name="📜 Log Channel",
        value=log_channel.mention if log_channel else "❌ Not set",
        inline=True
    )
    embed.add_field(
        name="🔔 Mirage Ping Role",
        value=mirage_role.mention if mirage_role else "❌ Not set",
        inline=True
    )
    embed.add_field(
        name="🔔 Normal Ping Role",
        value=normal_role.mention if normal_role else "❌ Not set",
        inline=True
    )
    embed.add_field(
        name="🔄 Auto-Updates",
        value=f"{'✅ Enabled' if guild_config['auto_update_enabled'] else '❌ Disabled'} ({guild_config['auto_check_interval']//60} min)",
        inline=True
    )
    embed.add_field(
        name="🎨 Embed Color",
        value=f"#{guild_config['embed_color']:06x}",
        inline=True
    )
    embed.add_field(
        name="🔒 Private Commands",
        value=", ".join(guild_config["private_commands"]) if guild_config["private_commands"] else "None",
        inline=True
    )
    view = SettingsView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.slash_command(description="Toggle auto stock updates")
async def toggleautoupdate(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    guild_config["auto_update_enabled"] = not guild_config["auto_update_enabled"]
    save_config(config_data)
    status = "enabled" if guild_config["auto_update_enabled"] else "disabled"
    await interaction.response.send_message(f"✅ Auto-updates {status}")

@bot.slash_command(description="Set auto-update interval")
async def setinterval(interaction: Interaction, minutes: int = SlashOption(description="Interval in minutes (5-120)", min_value=5, max_value=120)):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ Only bot owners can use this command!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    guild_config["auto_check_interval"] = minutes * 60
    save_config(config_data)
    await interaction.response.send_message(f"✅ Auto-update interval set to {minutes} minutes")

@bot.slash_command(description="Reload config file")
async def reload(interaction: Interaction):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ Only bot owners can use this command!", ephemeral=True)
        return

    global config_data
    config_data, _ = load_config()
    await interaction.response.send_message("✅ Config reloaded")






@bot.command(name="iventoryfruits", aliases=["inventory", "inv"])
async def inventory(ctx):
    inventory = load_inventory()
    user_id = str(ctx.author.id)
    
    if user_id not in inventory or not inventory[user_id]:
        embed = nextcord.Embed(
            title="🍎 Fruit Inventory",
            description="Your inventory is empty! Use `?rerollfruit` to get fruits.",
            color=default_guild_config["embed_color"]
        )
        embed.set_thumbnail(url="https://i.postimg.cc/8c8fkNsH/empty-inventory.png")
        embed.set_footer(text="Blox Fruits Bot | Use ?rerollfruit to get new fruits")
        await ctx.send(embed=embed)
        return
    
    # Count each fruit in inventory
    fruit_counts = {}
    for fruit in inventory[user_id]:
        fruit_counts[fruit] = fruit_counts.get(fruit, 0) + 1
    
    # Get total fruits and sort by rarity
    total_fruits = len(inventory[user_id])
    rarity_order = {"Common": 1, "Uncommon": 2, "Rare": 3, "Epic": 4, "Legendary": 5, "Mythical": 6}
    
    sorted_fruits = []
    for fruit_name, count in fruit_counts.items():
        # Find the fruit's rarity
        for fruit in FRUITS:
            if fruit["name"] == fruit_name:
                rarity = fruit["rarity"]
                rarity_value = rarity_order.get(rarity, 0)
                sorted_fruits.append((fruit_name, count, rarity, rarity_value))
                break
    
    # Sort by rarity (highest first)
    sorted_fruits.sort(key=lambda x: x[3], reverse=True)
    
    # Create fancy inventory display
    embed = nextcord.Embed(
        title="🍎 Fruit Inventory",
        description=f"You have **{total_fruits}** fruit{'s' if total_fruits != 1 else ''} in your inventory!",
        color=default_guild_config["embed_color"]
    )
    
    # Add fields for each rarity category
    rarity_emojis = {
        "Common": "<:Common_Loot_Crate:1362035849822212178>",
        "Uncommon": "<:Uncommon_Loot_Crate:1362035989836464159>",
        "Rare": "<:Rare_Loot_Crate:1362036146711826582>",
        "Epic": "<:Epic_Loot_Crate:1362036314161156246>",
        "Legendary": "<:Legendary_Scroll:1362036667455766559>",
        "Mythical": "<:mythical_scroll:1362036887564320768>-"
    }
    
    rarity_groups = {}
    for fruit_name, count, rarity, _ in sorted_fruits:
        if rarity not in rarity_groups:
            rarity_groups[rarity] = []
        rarity_groups[rarity].append(f"{fruit_name} x{count}")
    
    for rarity in ["Mythical", "Legendary", "Epic", "Rare", "Uncommon", "Common"]:
        if rarity in rarity_groups:
            emoji = rarity_emojis.get(rarity, "")
            fruits_text = "\n".join(rarity_groups[rarity])
            embed.add_field(
                name=f"{emoji} {rarity}",
                value=fruits_text,
                inline=False
            )
    
    # Calculate rarest fruit for thumbnail
    rarest_fruit = sorted_fruits[0][0] if sorted_fruits else None
    rarest_image = None
    
    if rarest_fruit:
        for fruit in FRUITS:
            if fruit["name"] == rarest_fruit and fruit.get("image"):
                rarest_image = fruit["image"]
                break
    
    if rarest_image:
        embed.set_thumbnail(url=rarest_image)
    
    embed.set_image(url="https://i.postimg.cc/76xQScQM/descarga.jpg")
    embed.set_footer(text="Blox Fruits Bot | Your Valuable Collection")
    await ctx.send(embed=embed)

@bot.slash_command(description="View top fruit collectors")
async def leaderboard(interaction: Interaction):
    guild_config = get_guild_config(interaction.guild_id)
    inventory = load_inventory()
    leaderboard = [(user_id, len(fruits)) for user_id, fruits in inventory.items()]
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    embed = nextcord.Embed(title="<:GD_Trophy:1362037482732126269> Fruit Collector Leaderboard", color=guild_config["embed_color"])
    embed.set_footer(text="Blox Fruits Bot")
    if not leaderboard:
        embed.description = "No collectors yet!"
    else:
        for i, (user_id, count) in enumerate(leaderboard[:10], 1):
            user = await bot.fetch_user(int(user_id))
            embed.add_field(
                name=f"{i}. {user.name}",
                value=f"Fruits: {count}",
                inline=False
            )
    await interaction.response.send_message(embed=embed)

@bot.slash_command(description="Send feedback or report bugs")
@commands.cooldown(1, 300, commands.BucketType.user)
async def feedback(interaction: Interaction, message: str = SlashOption(description="Your feedback or bug report")):
    guild_config = get_guild_config(interaction.guild_id)
    embed = nextcord.Embed(
        title="📬 Feedback Received",
        description=message[:2000],
        color=guild_config["embed_color"]
    )
    embed.add_field(name="User", value=interaction.user.mention, inline=True)
    embed.add_field(name="Guild", value=interaction.guild.name, inline=True)
    embed.set_footer(text="Blox Fruits Bot")

    if FEEDBACK_CHANNEL_ID:
        channel = bot.get_channel(FEEDBACK_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)
        else:
            await log_error(f"Feedback channel {FEEDBACK_CHANNEL_ID} not found!")
    else:
        for owner_id in OWNER_IDS:
            try:
                owner = await bot.fetch_user(owner_id)
                await owner.send(embed=embed)
            except:
                await log_error(f"Failed to DM owner {owner_id}")

    await interaction.response.send_message("✅ Thank you for your feedback!", ephemeral=True)

@bot.slash_command(description="Owner management menu")
async def ownermenu(interaction: Interaction):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ Only bot owners can use this command!", ephemeral=True)
        return
    guild_config = get_guild_config(interaction.guild_id)
    embed = nextcord.Embed(title="👑 Owner Menu", description="Select an action below", color=guild_config["embed_color"])
    view = OwnerView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.slash_command(description="Private test command for bot owners")
async def testbot(interaction: Interaction):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ This command is restricted to bot owners!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    embed = nextcord.Embed(
        title="🔧 Bot Test",
        description="This is a private test command for debugging and testing the bot.",
        color=guild_config["embed_color"]
    )
    embed.add_field(name="Test Status", value="Bot is running normally!", inline=False)
    embed.add_field(name="Guild ID", value=str(interaction.guild_id), inline=True)
    embed.add_field(name="User ID", value=str(interaction.user.id), inline=True)
    embed.set_footer(text="Blox Fruits Bot - Private Test")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.slash_command(description="Toggle private status of a command (Owner only)")
async def toggleprivate(
    interaction: Interaction,
    command_name: str = SlashOption(description="Command name to toggle private status")
):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ Only bot owners can use this command!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    private_commands = guild_config.get("private_commands", [])
    
    if command_name.lower() in private_commands:
        private_commands.remove(command_name.lower())
        status = "no longer private"
    else:
        private_commands.append(command_name.lower())
        status = "now private"
    
    guild_config["private_commands"] = private_commands
    save_config(config_data)
    
    await interaction.response.send_message(f"✅ Command `/{command_name}` is {status}!", ephemeral=True)

@bot.slash_command(description="View recent stock changes")
async def stockhistory(interaction: Interaction):
    guild_config = get_guild_config(interaction.guild_id)
    history = load_stock_history()
    guild_history = [entry for entry in history if entry.get("guild_id") == interaction.guild_id]
    if not guild_history:
        await interaction.response.send_message("❌ No stock history available for this server!", ephemeral=True)
        return
    try:
        latest = guild_history[-1]
        embed = create_detailed_stock_embed(
            latest.get("normal_stock", []),
            latest.get("mirage_stock", []),
            latest.get("changes"),
            embed_color=guild_config["embed_color"]
        )
        embed.title = f"📜 Stock Snapshot ({latest['timestamp']})"
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message("❌ Failed to load stock history!", ephemeral=True)
        await log_error(f"Stock history error: {str(e)}", interaction.guild_id)

@bot.slash_command(description="View stock change analytics")
async def stockanalytics(interaction: Interaction):
    guild_config = get_guild_config(interaction.guild_id)
    history = load_stock_history()
    guild_history = [entry for entry in history if entry.get("guild_id") == interaction.guild_id]
    if not guild_history:
        await interaction.response.send_message("❌ No analytics available!", ephemeral=True)
        return

    fruit_counts = defaultdict(int)
    for entry in guild_history:
        for stock_type in ["normal_stock", "mirage_stock"]:
            for item in entry.get(stock_type, []):
                if isinstance(item, str):
                    fruit_counts[item] += 1
                else:
                    fruit_counts[item.get("name", "Unknown")] += 1

    embed = nextcord.Embed(title="📈 Stock Analytics", color=guild_config["embed_color"])
    embed.description = "Fruit appearance frequency in stock history:"
    for fruit, count in sorted(fruit_counts.items(), key=lambda x: x[1], reverse=True):
        embed.add_field(name=fruit, value=f"Appeared {count} times", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.slash_command(description="Reset first-time setup")
async def resetsetup(interaction: Interaction):
    if interaction.user.id not in OWNER_IDS:
        await interaction.response.send_message("❌ Only bot owners can use this command!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    guild_config["first_setup"] = True
    save_config(config_data)
    await interaction.response.send_message("✅ First-time setup reset", ephemeral=True)

@bot.slash_command(description="Interactive bot setup")
async def setup(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions!", ephemeral=True)
        return

    guild_config = get_guild_config(interaction.guild_id)
    embed = nextcord.Embed(
        title="⚙️ Bot Setup",
        description="Use the menu below to configure the bot!",
        color=guild_config["embed_color"]
    )
    view = SetupView(interaction.guild_id)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# Economy commands
# Example for ?balance
@bot.command(name="balance")
async def balance(ctx):
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    berries = economy[user_id]["berries"]
    active_race = economy[user_id]["active_race"] or "None"
    embed = nextcord.Embed(
        title="<:Money:1362032925838934048> Balance",
        description=f"You have **{berries} Berries**.",
        color=0xFF0000
    )
    embed.add_field(name="Active Race", value=active_race)
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)

@bot.command(name="daily")
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    
    berries = 100
    if economy[user_id]["active_race"] == "Human":
        berries = int(berries * 1.10)  # +10% for Human
    if economy[user_id]["active_race"] == "Cyborg" and economy[user_id]["bank"] > 0:
        interest = int(economy[user_id]["bank"] * 0.05)  # 5% bank interest
        berries += interest
        economy[user_id]["berries"] += interest
    
    economy[user_id]["berries"] += berries
    economy[user_id]["last_daily"] = int(time.time())
    save_economy(economy)
    embed = nextcord.Embed(
        title="<:giveaways:1362038220325392474> Daily Reward",
        description=f"You claimed **{berries} Berries**!",
        color=0xFF0000
    )
    if economy[user_id]["active_race"] == "Cyborg" and interest:
        embed.add_field(name="Cyborg Bonus", value=f"+{interest} Berries from bank interest!")
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)


@bot.command(name="shop")
async def shop(ctx):
    embed = nextcord.Embed(title="<:PurpleTrolley:1362038374080450632> Berry Shop", color=default_guild_config["embed_color"])
    embed.set_footer(text="Blox Fruits Bot")
    for item_id, item in SHOP_ITEMS.items():
        embed.add_field(
            name=item["name"],
            value=f"**Price**: {item['price']} Berries\n**Description**: {item['description']}",
            inline=False
        )
    await ctx.send(embed=embed)

@bot.command(name="buy")
async def buy(ctx, item_id: str):
    item_id = item_id.lower()
    if item_id not in SHOP_ITEMS:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Invalid item! Use `?shop` to see available items.",
            color=0xFF0000
        ))
        return

    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0}

    item = SHOP_ITEMS[item_id]
    if economy[user_id]["berries"] < item["price"]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You need {item['price']} Berries to buy {item['name']}!",
            color=0xFF0000
        ))
        return

    economy[user_id]["berries"] -= item["price"]
    inventory = load_inventory()
    if user_id not in inventory:
        inventory[user_id] = []

    if item_id == "reroll_token":
        # Handled in rerollfruit
        pass
    elif item_id == "rare_fruit":
        rare_fruits = [f for f in FRUITS if f["rarity"] in ["Rare", "Legendary", "Mythical"]]
        selected_fruit = random.choice(rare_fruits)
        inventory[user_id].append(selected_fruit["name"])
        save_inventory(inventory)

    save_economy(economy)
    embed = nextcord.Embed(
        title="✅ Purchase Successful",
        description=f"You bought **{item['name']}** for {item['price']} Berries!",
        color=default_guild_config["embed_color"]
    )
    if item_id == "rare_fruit":
        embed.add_field(name="Fruit Received", value=selected_fruit["name"], inline=False)
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)

@bot.command(name="give")
async def give(ctx, member: nextcord.Member, amount: int):
    if amount <= 0:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Amount must be positive!",
            color=0xFF0000
        ))
        return
    if member.id == ctx.author.id:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="You can't give Berries to yourself!",
            color=0xFF0000
        ))
        return
    economy = load_economy()
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    if target_id not in economy:
        economy[target_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    if economy[user_id]["berries"] < amount:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You don't have {amount} Berries!",
            color=0xFF0000
        ))
        return
    
    economy[user_id]["berries"] -= amount
    if economy[user_id]["active_race"] == "Angel":
        bonus = int(amount * 0.25)  # +25% bonus
        economy[target_id]["berries"] += (amount + bonus)
        result = f"You gave {member.mention} **{amount} Berries** (+{bonus} Angel bonus)!"
    else:
        economy[target_id]["berries"] += amount
        result = f"You gave {member.mention} **{amount} Berries**!"
    
    save_economy(economy)
    embed = nextcord.Embed(
        title="<:giveaways:1362038220325392474> Gift Sent",
        description=result,
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)

@bot.command(name="rerollfruit")
@commands.cooldown(1, 30, commands.BucketType.user)
async def rerollfruit(ctx):
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0}
    if economy[user_id]["berries"] < 50:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="You need 50 Berries to reroll! Use ?daily to earn more.",
            color=0xFF0000
        ))
        return

    economy[user_id]["berries"] -= 50
    save_economy(economy)

    total_chance = sum(fruit["chance"] for fruit in FRUITS)
    rand = random.random() * total_chance
    current = 0
    selected_fruit = None
    for fruit in FRUITS:
        current += fruit["chance"]
        if rand <= current:
            selected_fruit = fruit
            break

    inventory = load_inventory()
    if user_id not in inventory:
        inventory[user_id] = []
    inventory[user_id].append(selected_fruit["name"])
    save_inventory(inventory)

    embed = nextcord.Embed(
        title="🎲 Fruit Reroll",
        description=f"You rolled **{selected_fruit['name']}**!\n**Rarity**: {selected_fruit['rarity']}\n**Chance**: {selected_fruit['chance']*100:.1f}%",
        color=default_guild_config["embed_color"]
    )
    if selected_fruit.get("image"):
        embed.set_thumbnail(url=selected_fruit["image"])
        embed.set_image(url="https://i.postimg.cc/76xQScQM/descarga.jpg")
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)

@bot.command(name="tradefruit")
@commands.cooldown(1, 60, commands.BucketType.user)
async def tradefruit(ctx, user: nextcord.Member, your_fruit: str, their_fruit: str):
    if user.id == ctx.author.id:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="You can't trade with yourself!",
            color=0xFF0000
        ))
        return

    inventory = load_inventory()
    user_id = str(ctx.author.id)
    target_id = str(user.id)

    if user_id not in inventory or your_fruit.lower() not in [f.lower() for f in inventory[user_id]]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You don't have **{your_fruit}** in your inventory!",
            color=0xFF0000
        ))
        return
    if target_id not in inventory or their_fruit.lower() not in [f.lower() for f in inventory[target_id]]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"{user.mention} doesn't have **{their_fruit}** in their inventory!",
            color=0xFF0000
        ))
        return

    embed = nextcord.Embed(
        title="🔄 Fruit Trade Proposal",
        description=(
            f"{ctx.author.mention} wants to trade **{your_fruit}** for {user.mention}'s **{their_fruit}**.\n"
            f"{user.mention}, do you accept this trade?"
        ),
        color=default_guild_config["embed_color"]
    )
    embed.set_footer(text="Blox Fruits Bot")
    view = TradeView(ctx.author, user, your_fruit, their_fruit)
    await ctx.send(embed=embed, view=view)




@bot.command(name="gamble")
@commands.cooldown(1, 30, commands.BucketType.user)
async def gamble(ctx, amount: int):
    if amount <= 0:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Amount must be positive!",
            color=0xFF0000
        ))
        return
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    if economy[user_id]["berries"] < amount:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You don't have {amount} Berries!",
            color=0xFF0000
        ))
        return
    
    win_chance = 0.50
    if economy[user_id]["active_race"] == "Mink":
        win_chance += 0.15  # +15% win chance
    
    if random.random() < win_chance:
        economy[user_id]["berries"] += amount
        result = f"You won **{amount * 2} Berries**!"
    else:
        economy[user_id]["berries"] -= amount
        result = f"You lost **{amount} Berries**!"
    save_economy(economy)
    embed = nextcord.Embed(
        title="🎰 Gamble Result",
        description=result,
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    embed.set_thumbnail(url="https://i.postimg.cc/sXYsgtGY/Money-Icon.webp")
    await ctx.send(embed=embed)

@bot.command(name="steal")
@commands.cooldown(1, 120, commands.BucketType.user)
async def steal(ctx, member: nextcord.Member):
    if member.id == ctx.author.id:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="You can't steal from yourself!",
            color=0xFF0000
        ))
        return
    
    economy = load_economy()
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    
    # Initialize user data
    if user_id not in economy:
        economy[user_id] = {
            "berries": 0,
            "last_daily": 0,
            "bank": 0,
            "races_owned": [],
            "active_race": None,
            "inventory": [],
            "boosts": {},
            "fruits": [],
            "haki": {"observation": {"level": 0, "exp": 0}, "armament": {"level": 0, "exp": 0}, "active_buff": None},
            "achievements": {"bosses_killed": 0, "steals_succeeded": 0, "daily_streak": 0, "berries_earned": 0}
        }
    if target_id not in economy:
        economy[target_id] = {
            "berries": 0,
            "last_daily": 0,
            "bank": 0,
            "races_owned": [],
            "active_race": None,
            "inventory": [],
            "boosts": {},
            "fruits": [],
            "haki": {"observation": {"level": 0, "exp": 0}, "armament": {"level": 0, "exp": 0}, "active_buff": None},
            "achievements": {"bosses_killed": 0, "steals_succeeded": 0, "daily_streak": 0, "berries_earned": 0}
        }
    
    if economy[target_id]["berries"] < 10:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"{member.mention} doesn't have enough Berries to steal!",
            color=0xFF0000
        ))
        return
    
    success_chance = 0.30
    if economy[user_id]["active_race"] == "Ghoul":
        success_chance += 0.30
    # Haki boosts
    observation_level = economy[user_id]["haki"]["observation"]["level"]
    success_chance += 0.05 * observation_level  # +5% per level
    if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
        success_chance += 0.10 * observation_level  # +10% per level when active
    
    if random.random() < success_chance:
        stolen = random.randint(10, 30)
        stolen = min(stolen, economy[target_id]["berries"])
        economy[user_id]["berries"] += stolen
        economy[target_id]["berries"] -= stolen
        economy[user_id]["achievements"]["steals_succeeded"] += 1
        economy[user_id]["achievements"]["berries_earned"] += stolen
        result = f"You stole **{stolen} Berries** from {member.mention}!"
    else:
        fine = random.randint(5, 15)
        economy[user_id]["berries"] = max(0, economy[user_id]["berries"] - fine)
        result = f"You got caught and paid **{fine} Berries** as a fine!"
    
    save_economy(economy)
    embed = nextcord.Embed(
        title="🕵️ Steal Attempt",
        description=result,
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)


@bot.command(name="deposit")
async def deposit(ctx, amount: int):
    if amount <= 0:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Amount must be positive!",
            color=0xFF0000
        ))
        return
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0}
    if economy[user_id]["berries"] < amount:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You don't have {amount} Berries!",
            color=0xFF0000
        ))
        return
    economy[user_id]["berries"] -= amount
    economy[user_id]["bank"] += amount
    save_economy(economy)
    embed = nextcord.Embed(
        title="🏦 Deposit Successful",
        description=f"You deposited **{amount} Berries** into your bank!",
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)



@bot.command(name="bank")
async def bank(ctx):
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0}
    bank_balance = economy[user_id]["bank"]
    embed = nextcord.Embed(
        title="🏦 Bank Balance",
        description=f"You have **{bank_balance} Berries** in your bank.",
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    embed.set_thumbnail(url="https://i.postimg.cc/sXYsgtGY/Money-Icon.webp")
    await ctx.send(embed=embed)




@bot.command(name="shoprace")
async def shop(ctx):
    shop_items = {
        "reroll_token": {"name": "Reroll Token", "price": 50, "description": "Grants one fruit reroll"},
        "human_race": {"name": "Human Race", "price": 100, "description": "+10% Berries from ?daily"},
        "shark_race": {"name": "Shark Race", "price": 300, "description": "+20% Berries from ?work"},
        "mink_race": {"name": "Mink Race", "price": 350, "description": "+15% win chance in ?gamble"},
        "angel_race": {"name": "Angel Race", "price": 400, "description": "+25% Berries when using ?give"},
        "ghoul_race": {"name": "Ghoul Race", "price": 1000, "description": "+30% success rate in ?steal"},
        "cyborg_race": {"name": "Cyborg Race", "price": 1000, "description": "+50% bank interest via ?daily"}
    }
    embed = nextcord.Embed(title="🛒 Blox Fruits Shop", color=0xFF0000)
    for item_id, item in shop_items.items():
        embed.add_field(
            name=f"{item['name']} - {item['price']} Berries",
            value=item['description'],
            inline=False
        )
    embed.set_footer(text="Use ?buy <item> to purchase!")
    await ctx.send(embed=embed)



@bot.command(name="buyrace")
async def buy(ctx, *, item_name):
    shop_items = {
        "reroll_token": {"name": "Reroll Token", "price": 50, "description": "Grants one fruit reroll"},
        "human_race": {"name": "Human Race", "price": 100, "description": "+10% Berries from ?daily"},
        "shark_race": {"name": "Shark Race", "price": 300, "description": "+20% Berries from ?work"},
        "mink_race": {"name": "Mink Race", "price": 350, "description": "+15% win chance in ?gamble"},
        "angel_race": {"name": "Angel Race", "price": 400, "description": "+25% Berries when using ?give"},
        "ghoul_race": {"name": "Ghoul Race", "price": 1000, "description": "+30% success rate in ?steal"},
        "cyborg_race": {"name": "Cyborg Race", "price": 1000, "description": "+50% bank interest via ?daily"}
    }
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    
    item_id = None
    for key, item in shop_items.items():
        if item["name"].lower() == item_name.lower():
            item_id = key
            break
    
    if not item_id:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Item not found in shop!",
            color=0xFF0000
        ))
        return
    
    item = shop_items[item_id]
    if economy[user_id]["berries"] < item["price"]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You need {item['price']} Berries to buy {item['name']}!",
            color=0xFF0000
        ))
        return
    
    if item_id.endswith("_race"):
        race_name = item["name"].replace(" Race", "")
        if race_name in economy[user_id]["races_owned"]:
            await ctx.send(embed=nextcord.Embed(
                title="❌ Error",
                description=f"You already own the {race_name} race!",
                color=0xFF0000
            ))
            return
        economy[user_id]["races_owned"].append(race_name)
        if not economy[user_id]["active_race"]:
            economy[user_id]["active_race"] = race_name
    else:
        # Handle non-race items (e.g., reroll_token)
        economy[user_id].setdefault("inventory", []).append(item_id)
    
    economy[user_id]["berries"] -= item["price"]
    save_economy(economy)
    embed = nextcord.Embed(
        title="✅ Purchase Successful",
        description=f"You bought {item['name']} for {item['price']} Berries!",
        color=0xFF0000
    )
    if item_id.endswith("_race"):
        embed.add_field(name="Tip", value=f"Use ?userace {race_name} to activate it!")
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)




@bot.command(name="userace")
async def userace(ctx, *, race_name):
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {"berries": 0, "last_daily": 0, "bank": 0, "races_owned": [], "active_race": None}
    
    race_name = race_name.title()
    if race_name not in ["Human", "Shark", "Mink", "Angel", "Ghoul", "Cyborg"]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Invalid race! Choose from: Human, Shark, Mink, Angel, Ghoul, Cyborg",
            color=0xFF0000
        ))
        return
    
    if race_name not in economy[user_id]["races_owned"]:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description=f"You don't own the {race_name} race! Buy it with ?buy {race_name} Race",
            color=0xFF0000
        ))
        return
    
    economy[user_id]["active_race"] = race_name
    save_economy(economy)
    embed = nextcord.Embed(
        title="🧬 Race Activated",
        description=f"You are now a **{race_name}**!",
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)   





class HelpView(View):
    def __init__(self, user_id):
        super().__init__(timeout=60)
        self.user_id = user_id

        economy_button = Button(label="Economy", style=nextcord.ButtonStyle.green, emoji="💰")
        economy_button.callback = self.economy_callback
        self.add_item(economy_button)

        combat_button = Button(label="Combat", style=nextcord.ButtonStyle.red, emoji="⚔️")
        combat_button.callback = self.combat_callback
        self.add_item(combat_button)

        haki_button = Button(label="Haki & Profile", style=nextcord.ButtonStyle.blurple, emoji="🌀")
        haki_button.callback = self.haki_callback
        self.add_item(haki_button)

        adventure_button = Button(label="Adventure", style=nextcord.ButtonStyle.grey, emoji="🗺️")
        adventure_button.callback = self.adventure_callback
        self.add_item(adventure_button)

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user.id == self.user_id

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def economy_callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🏴‍☠️ Economy Commands",
            description="🌊 Manage your Berries, pirate!\n══════",
            color=0xFFD700
        )
        commands = [
            ("?balance", "Check your Berries"),
            ("?daily", "Claim 100 Berries daily"),
            ("?shop", "View the shop"),
            ("?buy <item>", "Buy an item (e.g., ?buy Human Race)"),
            ("?give <@user> <amount>", "Give Berries to another user"),
            ("?work", "Earn 20-50 Berries (1-hour cooldown)"),
            ("?gamble <amount>", "Bet Berries to double or lose"),
            ("?steal <@user>", "Try to steal Berries (2-min cooldown)"),
            ("?richest", "Show top 5 richest users"),
            ("?deposit <amount>", "Store Berries in your bank"),
            ("?withdraw <amount>", "Take Berries from your bank"),
            ("?bank", "Check your bank"),
            ("?rerollfruit", "Spend 50 Berries for a random fruit"),
            ("?tradefruit <@user> <your_fruit> <their_fruit>", "Trade fruits")
        ]
        for cmd, desc in commands:
            embed.add_field(name=cmd, value=desc, inline=False)
        embed.set_footer(text="One Piece Adventure")
        await interaction.response.edit_message(embed=embed, view=self)

    async def combat_callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="⚔️ Combat Commands",
            description="🌊 Fight for loot, pirate!\n══════",
            color=0xFF0000
        )
        commands = [
            ("?kill <boss_name>", "Defeat the active boss"),
            ("?killpirate", "Fight a pirate for Berries and loot"),
            ("?killmarine", "Battle a marine for Berries and loot"),
            ("?killseabeast", "Slay a sea beast for Berries and loot"),
            ("?huntbandit", "Hunt a bandit for Berries and loot"),
            ("?bountyhunt", "Chase a wanted pirate for big rewards"),
            ("?arena", "Duel another player in the arena")
        ]
        for cmd, desc in commands:
            embed.add_field(name=cmd, value=desc, inline=False)
        embed.set_footer(text="One Piece Adventure")
        await interaction.response.edit_message(embed=embed, view=self)

    async def haki_callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🌀 Haki & Profile Commands",
            description="🌊 Master your Haki, pirate!\n══════",
            color=0x4B0082
        )
        commands = [
            ("?trainhaki <type>", "Train Observation or Armament Haki (100 Berries)"),
            ("?usehaki <type>", "Activate a Haki buff for 10 minutes"),
            ("?profile [@user]", "View your or another’s profile"),
            ("?userace <race>", "Activate a purchased race"),
            ("?races", "Check race benefits")
        ]
        for cmd, desc in commands:
            embed.add_field(name=cmd, value=desc, inline=False)
        embed.set_footer(text="One Piece Adventure")
        await interaction.response.edit_message(embed=embed, view=self)

    async def adventure_callback(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🗺️ Adventure Commands",
            description="🌊 Explore the seas, pirate!\n══════",
            color=0x2A4B7C
        )
        commands = [
            ("?exploreisland", "Discover treasures or dangers on an island"),
            ("?trade <@user> <your_item> <their_item>", "Swap items with another pirate"),
            ("?fish", "Cast your line for Berries or rare items"),
            ("?raid", "Join a group assault on a marine fortress"),
            ("?huntreasure", "Search for a legendary treasure chest"),
            ("?navalbattle", "Command your ship in a cannon fight"),
            ("?solveriddle", "Solve a pirate riddle for rewards"),
            ("?formcrew", "Create or join a pirate crew for bonuses")
        ]
        for cmd, desc in commands:
            embed.add_field(name=cmd, value=desc, inline=False)
        embed.set_footer(text="One Piece Adventure")
        await interaction.response.edit_message(embed=embed, view=self)











@bot.slash_command(description="Get a Blox Fruits meme")
async def memefruit(interaction: Interaction, use_api: bool = SlashOption(description="Use meme API? (Images, not Blox Fruits specific)", default=False)):
    await interaction.response.defer()
    guild_config = get_guild_config(interaction.guild_id)
    
    if use_api:
        # Opción con Meme API (imágenes genéricas)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as response:
                if response.status == 200:
                    data = await response.json()
                    meme_text = data.get("title", "Random Meme")
                    meme_url = data.get("url", "")
                    embed = nextcord.Embed(title="😂 Random Meme", description=meme_text, color=guild_config["embed_color"])
                    if meme_url:
                        embed.set_image(url=meme_url)
                else:
                    embed = nextcord.Embed(title="😂 Meme Error", description="Couldn't fetch a meme! Try again.", color=guild_config["embed_color"])
    else:
        # Lista estática de 50 memes de Blox Fruits
        memes = [
            "When you grind for 10 hours and get a Rocket fruit... 🚀💥",
            "Me trying to dodge a Kitsune combo: 🏃‍♂️💨",
            "Darkbeard: *exists* My inventory: *empty* 😭",
            "When you finally get Dragon but die to a noob with Chop: 🐉💀",
            "Grinding to 15M bounty just to lose it in one PvP: 😢",
            "Me after missing Mirage Island for the 5th time: 🏝️😩",
            "When you use Buddha to grind but still get one-shot: 🧘‍♂️💥",
            "Spending all your berries on a Spin fruit: 💸🙃",
            "When the server lags during a Sea Beast fight: 🌊📉",
            "Me pretending I know how to combo with Light: 💡🤡",
            "When you get a Mythical fruit but no robux to awaken it: 😭",
            "Trying to trade a Spike for a Dragon: 🤝❌",
            "When you join a server and it’s full of hackers: 😤",
            "Me after failing to solo Factory 10 times: 🏭😓",
            "When you get Ice but keep falling in water: 🧊🌊",
            "Spending 1M berries on a boat just to sink it: 🚤💦",
            "When your friend betrays you for a Leopard fruit: 🐆🔪",
            "Me trying to aim with Quake in PvP: 🌍🤔",
            "When you finally awaken Flame but servers crash: 🔥😑",
            "Grinding for 2 hours and getting 1k berries: 💪💸",
            "When you see a Kitsune user and know you’re doomed: 🦊💀",
            "Me after losing 10M bounty to a random: 😡",
            "When you roll a fruit and it’s Spring... again: 🌸😞",
            "Trying to find Third Sea without dying: 🗺️💥",
            "When you get Magma but forget how to use it: 🌋🤷‍♂️",
            "Me after getting killed by a level 1 with Bomb: 💣😵",
            "When you spend all day grinding and mom says ‘turn off the game’: 😭",
            "Joining a server just as Mirage Island despawns: 🏝️😢",
            "When you master Dark but everyone uses Light: 🌑💡",
            "Me trying to convince my friend Chop is good: 🍎🤡",
            "When you get a Legendary fruit but no moves left: 🎉😩",
            "Spending 500 robux on spins and getting Kilo: 💸🙄",
            "When you fight a boss and lag spikes: 🦁📉",
            "Me after losing to a Dough user in 2 seconds: 🍩💀",
            "When you grind for T-Rex and get Falcon instead: 🦖🦅",
            "Trying to trade up to a Mythical with a Common: 🤝😂",
            "When you awaken your fruit but forget the combo: 💪🤔",
            "Me after dying to a shark in Second Sea: 🦈😓",
            "When you get a good fruit but no friends to flex: 😎😞",
            "Spending all your berries on a gamepass that’s useless: 💳😑",
            "When you finally hit max level but still suck at PvP: 🎉🤡",
            "Me trying to solo Darkbeard with a Rare fruit: 🦁💥",
            "When the game updates and your build is nerfed: 📜😭",
            "Grinding for 5 hours and forgetting to save fruit: 🍎😢",
            "When you get a fruit but it’s unawakened and useless: 😴",
            "Me after missing a Sea Event by 1 second: 🌊😩",
            "When you trade your best fruit for a scam: 🤝💸",
            "Trying to learn combos from YouTube at 3 AM: 📹🥱",
            "When you get a Mythical but your PC crashes: 🖥️💥",
            "Me after getting one-shot by a random in Third Sea: 😵"
        ]
        meme = random.choice(memes)
        embed = nextcord.Embed(title="😂 Blox Fruits Meme", description=meme, color=guild_config["embed_color"])
    
    # Enviar el embed y añadir reacciones
    message = await interaction.followup.send(embed=embed)
    w_emoji = nextcord.utils.get(interaction.guild.emojis, name="W") or "🇼"
    l_emoji = nextcord.utils.get(interaction.guild.emojis, name="L") or "🇱"
    await message.add_reaction(w_emoji)
    await message.add_reaction(l_emoji)








@bot.command(name="helpBlox")
async def helpBlox(ctx):
    try:
        embed = nextcord.Embed(
            title="Help Menu",
            description="🌊 Choose a category, captain!\n══════",
            color=0xFFD700
        )
        embed.set_footer(text="One Piece Adventure | Menu active for 60 seconds")
        view = HelpView(ctx.author.id)
        message = await ctx.send(embed=embed, view=view)
        view.message = message
    except Exception as e:
        print(f"Error in helpBlox for user {ctx.author.id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Map’s torn, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))

@bot.slash_command(name="setchannelrandomboss", description="Set the channel for random boss spawns (admin only)")
@commands.has_permissions(administrator=True)
async def set_channel_random_boss(interaction: nextcord.Interaction, channel: nextcord.TextChannel):
    boss_config = load_boss_config()
    guild_id = str(interaction.guild.id)
    if guild_id not in boss_config:
        boss_config[guild_id] = {"boss_channel": None, "active_boss": None, "last_spawn": 0}
    boss_config[guild_id]["boss_channel"] = str(channel.id)
    save_boss_config(boss_config)
    embed = nextcord.Embed(
        title="✅ Boss Channel Set",
        description=f"Random bosses will spawn in {channel.mention}.",
        color=0xFF0000
    )
    embed.set_footer(text="Blox Fruits Bot")
    await interaction.response.send_message(embed=embed)




BOSSES = [
    {"name": "Gorilla King", "difficulty": "Easy", "image": "https://blox-fruits.fandom.com/wiki/Gorilla_King#/media/File:Gorilla_King.png", "rewards": {"berries": (50, 100), "items": [("Crown Shard", 0.05)]}},
    {"name": "Bobby", "difficulty": "Easy", "image": "https://blox-fruits.fandom.com/wiki/Bobby#/media/File:Bobby.png", "rewards": {"berries": (50, 100), "items": [("Chop Fruit Shard", 0.05)]}},
    {"name": "Yeti", "difficulty": "Easy", "image": "https://blox-fruits.fandom.com/wiki/Yeti#/media/File:Yeti.png", "rewards": {"berries": (50, 100), "items": [("Snow Pelt", 0.05)]}},
    {"name": "Vice Admiral", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Vice_Admiral#/media/File:Vice_Admiral.png", "rewards": {"berries": (100, 200), "items": [("Admiral Coat", 0.10)]}},
    {"name": "Warden", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Warden#/media/File:Warden.png", "rewards": {"berries": (100, 200), "items": [("Prison Key", 0.10)]}},
    {"name": "Magma Admiral", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Magma_Admiral#/media/File:Magma_Admiral.png", "rewards": {"berries": (100, 200), "items": [("Refined Musket", 0.10)]}},
    {"name": "Fishman Lord", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Fishman_Lord#/media/File:Fishman_Lord.png", "rewards": {"berries": (200, 300), "items": [("Trident", 0.15)]}},
    {"name": "Wysper", "difficulty": "Easy", "image": "https://blox-fruits.fandom.com/wiki/Wysper#/media/File:Wysper.png", "rewards": {"berries": (50, 100), "items": [("Bazooka", 0.05)]}},
    {"name": "Thunder God", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Thunder_God#/media/File:Thunder_God.png", "rewards": {"berries": (100, 200), "items": [("Pole (1st Form)", 0.10)]}},
    {"name": "Cyborg", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Cyborg_(Boss)#/media/File:Cyborg.png", "rewards": {"berries": (100, 200), "items": [("Cool Shades", 0.10)]}},
    {"name": "Diamond", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Diamond_(Boss)#/media/File:Diamond.png", "rewards": {"berries": (100, 200), "items": [("Longsword", 0.10)]}},
    {"name": "Fajita", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Fajita#/media/File:Fajita.png", "rewards": {"berries": (200, 300), "items": [("Gravity Cane", 0.15)]}},
    {"name": "Don Swan", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Don_Swan#/media/File:Don_Swan.png", "rewards": {"berries": (200, 300), "items": [("Swan Glasses", 0.15)]}},
    {"name": "Beautiful Pirate", "difficulty": "Medium", "image": "https://blox-fruits.fandom.com/wiki/Beautiful_Pirate#/media/File:Beautiful_Pirate.png", "rewards": {"berries": (100, 200), "items": [("Canvander", 0.10)]}},
    {"name": "Longma", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Longma#/media/File:Longma.png", "rewards": {"berries": (200, 300), "items": [("Tushita", 0.15)]}},
    {"name": "Cake Queen", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Cake_Queen#/media/File:Cake_Queen.png", "rewards": {"berries": (200, 300), "items": [("Buddy Sword", 0.15)]}},
    {"name": "Tide Keeper", "difficulty": "Hard", "image": "https://blox-fruits.fandom.com/wiki/Tide_Keeper#/media/File:Tide_Keeper.png", "rewards": {"berries": (200, 300), "items": [("Dragon Trident", 0.15)]}},
    {"name": "Greybeard", "difficulty": "Raid", "image": "https://blox-fruits.fandom.com/wiki/Greybeard#/media/File:Greybeard.png", "rewards": {"berries": (300, 500), "items": [("Bisento V2 Shard", 0.20)]}},
    {"name": "Darkbeard", "difficulty": "Raid", "image": "https://blox-fruits.fandom.com/wiki/Darkbeard#/media/File:Darkbeard.png", "rewards": {"berries": (300, 500), "items": [("Rare Artifact", 0.20)]}},
    {"name": "Dough King", "difficulty": "Raid", "image": "https://blox-fruits.fandom.com/wiki/Dough_King#/media/File:Dough_King.png", "rewards": {"berries": (300, 500), "items": [("Mirror Fractal", 0.25)]}}
]

@tasks.loop(minutes=1)
async def spawn_random_boss():
    boss_config = load_boss_config()
    for guild_id, config in boss_config.items():
        if not config.get("boss_channel"):
            continue
        if config.get("active_boss"):
            if time.time() - config["active_boss"]["spawn_time"] > 600:  # 10 minutes
                config["active_boss"] = None
                save_boss_config(boss_config)
            continue
        if time.time() - config.get("last_spawn", 0) < random.randint(900, 3600):  # 15–60 min
            continue
        boss = random.choice(BOSSES)
        config["active_boss"] = {"name": boss["name"], "spawn_time": time.time()}
        config["last_spawn"] = time.time()
        save_boss_config(boss_config)
        channel = bot.get_channel(int(config["boss_channel"]))
        if not channel:
            continue
        embed = nextcord.Embed(
            title=f"⚔️ Boss Spawned: {boss['name']}",
            description=f"A **{boss['name']}** ({boss['difficulty']}) has appeared!\nUse `?kill {boss['name']}` to defeat it!\nDespawns in 10 minutes.",
            color=0xFF0000
        )
        embed.set_image(url=boss["image"])
        embed.set_footer(text="Blox Fruits Bot")
        await channel.send(embed=embed)









@bot.command(name="kill")
@commands.cooldown(1, 30, commands.BucketType.user)
async def kill_boss(ctx, *, boss_name):
    boss_config = load_boss_config()
    guild_id = str(ctx.guild.id)
    if guild_id not in boss_config or not boss_config[guild_id].get("active_boss"):
        await ctx.send(embed=nextcord.Embed(
            title="❌ No Boss",
            description="No boss is active right now!",
            color=0xFF0000
        ))
        return
    
    active_boss = boss_config[guild_id]["active_boss"]
    if active_boss["name"].lower() != boss_name.lower():
        await ctx.send(embed=nextcord.Embed(
            title="❌ Wrong Boss",
            description=f"Use `?kill {active_boss['name']}` to fight the active boss!",
            color=0xFF0000
        ))
        return
    
    economy = load_economy()
    user_id = str(ctx.author.id)
    if user_id not in economy:
        economy[user_id] = {
            "berries": 0,
            "last_daily": 0,
            "bank": 0,
            "races_owned": [],
            "active_race": None,
            "inventory": [],
            "boosts": {},
            "fruits": [],
            "haki": {"observation": {"level": 0, "exp": 0}, "armament": {"level": 0, "exp": 0}, "active_buff": None},
            "achievements": {"bosses_killed": 0, "steals_succeeded": 0, "daily_streak": 0, "berries_earned": 0}
        }
    
    boss = next((b for b in BOSSES if b["name"] == active_boss["name"]), None)
    if not boss:
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Boss data not found!",
            color=0xFF0000
        ))
        return
    
    berries = random.randint(*boss["rewards"]["berries"])
    if economy[user_id]["active_race"] == "Human":
        berries = int(berries * 1.10)
    # Haki boost
    armament_level = economy[user_id]["haki"]["armament"]["level"]
    berries = int(berries * (1 + 0.10 * armament_level))
    if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "armament" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
        berries = int(berries * (1 + 0.20 * armament_level))
    
    items = []
    for item, chance in boss["rewards"]["items"]:
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        modified_chance = chance * (1 + 0.05 * observation_level)  # +5% per level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            modified_chance *= (1 + 0.10 * observation_level)
        if random.random() < modified_chance:
            items.append(item)
            economy[user_id]["inventory"].append(item)
    if random.random() < 0.05:
        economy[user_id]["boosts"]["work_2x"] = time.time() + 3600
        items.append("2x Work Boost (1 hour)")
    
    economy[user_id]["berries"] += berries
    economy[user_id]["achievements"]["bosses_killed"] += 1
    economy[user_id]["achievements"]["berries_earned"] += berries
    save_economy(economy)
    
    boss_config[guild_id]["active_boss"] = None
    save_boss_config(boss_config)
    
    embed = nextcord.Embed(
        title=f"🏆 {boss['name']} Defeated!",
        description=f"{ctx.author.mention} has slain **{boss['name']}** ({boss['difficulty']})!",
        color=0xFF0000
    )
    embed.add_field(name="Rewards", value=f"**{berries} Berries**\n" + ("\n".join(items) or "No items"))
    embed.set_footer(text="Blox Fruits Bot")
    await ctx.send(embed=embed)





@bot.command(name="trainhaki")
@commands.cooldown(1, 100, commands.BucketType.user)
async def train_haki(ctx, haki_type: str):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        
        # Initialize user data if missing
        if user_id not in economy:
            economy[user_id] = {
                "berries": 0,
                "last_daily": 0,
                "bank": 0,
                "races_owned": [],
                "active_race": None,
                "inventory": [],
                "boosts": {},
                "fruits": [],
                "haki": {"observation": {"level": 0, "exp": 0}, "armament": {"level": 0, "exp": 0}, "active_buff": None},
                "achievements": {"bosses_killed": 0, "steals_succeeded": 0, "daily_streak": 0, "berries_earned": 0}
            }
        # Ensure haki field exists
        if "haki" not in economy[user_id]:
            economy[user_id]["haki"] = {
                "observation": {"level": 0, "exp": 0},
                "armament": {"level": 0, "exp": 0},
                "active_buff": None
            }
        
        haki_type = haki_type.lower()
        if haki_type not in ["observation", "armament"]:
            await ctx.send(embed=nextcord.Embed(
                title="❌ Error",
                description="Choose 'observation' or 'armament'!",
                color=0xFF0000
            ))
            return
        
        if economy[user_id]["berries"] < 100:
            await ctx.send(embed=nextcord.Embed(
                title="❌ Error",
                description="You need 100 Berries to train!",
                color=0xFF0000
            ))
            return
        
        economy[user_id]["berries"] -= 100
        exp_gained = random.randint(10, 20)
        economy[user_id]["haki"][haki_type]["exp"] += exp_gained
        if economy[user_id]["haki"][haki_type]["exp"] >= 100 and economy[user_id]["haki"][haki_type]["level"] < 5:
            economy[user_id]["haki"][haki_type]["level"] += 1
            economy[user_id]["haki"][haki_type]["exp"] = 0
            await ctx.send(embed=nextcord.Embed(
                title="🌟 Haki Leveled Up!",
                description=f"Your {haki_type.title()} Haki is now Level {economy[user_id]['haki'][haki_type]['level']}!",
                color=0xFF0000
            ))
        else:
            await ctx.send(embed=nextcord.Embed(
                title="💪 Training Complete",
                description=f"Gained {exp_gained} EXP for {haki_type.title()} Haki!\nCurrent: {economy[user_id]['haki'][haki_type]['exp']}/100 EXP",
                color=0xFF0000
            ))
        
        save_economy(economy)
    except Exception as e:
        print(f"Error in trainhaki for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Something went wrong! Try again later.",
            color=0xFF0000
        ))



@bot.command(name="usehaki")
@commands.cooldown(1, 200, commands.BucketType.user)
async def use_haki(ctx, haki_type: str):
    economy = load_economy()
    user_id = str(ctx.author.id)
    haki_type = haki_type.lower()
    if haki_type not in ["observation", "armament"] or economy[user_id]["haki"][haki_type]["level"] == 0:
        await ctx.send(embed=nextcord.Embed(title="❌ Error", description="Invalid or untrained Haki!", color=0xFF0000))
        return
    
    economy[user_id]["haki"]["active_buff"] = {"type": haki_type, "expires": time.time() + 600}  # 10 min
    save_economy(economy)
    await ctx.send(embed=nextcord.Embed(title="🌀 Haki Activated", description=f"{haki_type.title()} Haki active for 10 minutes!", color=0xFF0000))









@bot.command(name="killseabeast")
@commands.cooldown(1, 60, commands.BucketType.user)  # 30-min cooldown
async def kill_seabeast(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.50
        if economy[user_id]["active_race"] == "Shark":
            success_chance += 0.20
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.05
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(title="🌊 Sea Beast Fight", color=0xFF0000)
        if random.random() < success_chance:
            berries = random.randint(100, 200)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "armament" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
                berries = int(berries * (1 + 0.20 * armament_level))
            
            items = []
            item_chance = 0.10
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Beast Core")
                economy[user_id]["inventory"].append("Beast Core")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"].setdefault("seabeasts_killed", 0)
            economy[user_id]["achievements"]["seabeasts_killed"] += 1
            
            embed.description = f"You defeated a sea beast!\n**Rewards**: {berries} Berries" + (f"\n**Items**: {', '.join(items)}" if items else "")
            await ctx.send(embed=embed)
            await ctx.author.send(embed=nextcord.Embed(
                title="🌊 Sea Beast Killed!",
                description="You’ve conquered a sea beast! Check your rewards in the channel.",
                color=0xFF0000
            ))
        else:
            embed.description = "The sea beast escaped! Try again later."
            await ctx.send(embed=embed)
        
        save_economy(economy)
    except Exception as e:
        print(f"Error in killseabeast for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Something went wrong! Try again later.",
            color=0xFF0000
        ))






@bot.command(name="killpirate")
@commands.cooldown(1, 10, commands.BucketType.user)
async def kill_pirate(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.60
        if economy[user_id]["active_race"] == "Ghoul":
            success_chance += 0.30
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.05
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(title="🏴‍☠️ Pirate Fight", color=0xFF0000)
        if random.random() < success_chance:
            berries = random.randint(50, 100)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "armament" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
                berries = int(berries * (1 + 0.20 * armament_level))
            
            items = []
            item_chance = 0.05
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Pirate Saber")
                economy[user_id]["inventory"].append("Pirate Saber")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"]["pirates_killed"] += 1
            
            embed.description = f"You defeated a pirate!\n**Rewards**: {berries} Berries" + (f"\n**Items**: {', '.join(items)}" if items else "")
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Pirate Killed!",
                    description="You’ve slain a pirate! Check your rewards in the channel.",
                    color=0xFF0000
                ))
            except:
                pass  # Ignore DM errors
        else:
            embed.description = "The pirate escaped! Try again later."
            await ctx.send(embed=embed)
        
        save_economy(economy)
    except Exception as e:
        print(f"Error in killpirate for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Something went wrong! Try again later.",
            color=0xFF0000
        ))






@bot.command(name="huntbandit")
@commands.cooldown(1, 300, commands.BucketType.user)  # 5-min cooldown
async def hunt_bandit(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.70
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.05
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(title="🗡️ Bandit Hunt", color=0xFF0000)
        if random.random() < success_chance:
            berries = random.randint(20, 50)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "armament" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
                berries = int(berries * (1 + 0.20 * armament_level))
            
            items = []
            item_chance = 0.03
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Bandit Knife")
                economy[user_id]["inventory"].append("Bandit Knife")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"].setdefault("bandits_killed", 0)
            economy[user_id]["achievements"]["bandits_killed"] += 1
            
            embed.description = f"You defeated a bandit!\n**Rewards**: {berries} Berries" + (f"\n**Items**: {', '.join(items)}" if items else "")
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🗡️ Bandit Killed!",
                    description="You’ve taken down a bandit! Check your rewards.",
                    color=0xFF0000
                ))
            except:
                pass
        else:
            embed.description = "The bandit got away! Try again later."
            await ctx.send(embed=embed)
        
        save_economy(economy)
    except Exception as e:
        print(f"Error in huntbandit for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Something went wrong! Try again later.",
            color=0xFF0000
        ))








@bot.command(name="huntreasure")
@commands.cooldown(1, 100, commands.BucketType.user)
async def hunt_treasure(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.60
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.10
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(
            title="🏴‍☠️ Treasure Hunt",
            description="🌊 You set sail for a legendary chest!\n══════",
            color=0x2A4B7C
        )
        if random.random() < success_chance:
            berries = random.randint(70, 150)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            
            items = []
            item_chance = 0.08
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Golden Compass")
                economy[user_id]["inventory"].append("Golden Compass")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"]["treasures_found"] += 1
            
            embed.description = f"🌊 You found the treasure!\n**Loot**: {berries} Berries" + (f"\n**Relics**: {', '.join(items)}" if items else "") + "\n══════"
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Treasure Claimed!",
                    description="🌊 You’ve unearthed a legendary chest! Check your loot.\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
            except:
                pass
        else:
            loss = random.randint(20, 50)
            economy[user_id]["berries"] = max(0, economy[user_id]["berries"] - loss)
            embed.description = f"🌊 A trap sprung! You lost {loss} Berries.\n══════"
            await ctx.send(embed=embed)
        
        embed.set_footer(text="One Piece Adventure")
        save_economy(economy)
    except Exception as e:
        print(f"Error in huntreasure for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))



@bot.command(name="exploreisland")
@commands.cooldown(1, 200, commands.BucketType.user)
async def explore_island(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.70
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.10
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(
            title="🏴‍☠️ Island Exploration",
            description="🌊 You sail to a mysterious island!\n══════",
            color=0x2A4B7C
        )
        if random.random() < success_chance:
            berries = random.randint(30, 80)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            
            items = []
            item_chance = 0.05
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Ancient Relic")
                economy[user_id]["inventory"].append("Ancient Relic")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"]["islands_explored"] += 1
            
            embed.description = f"🌊 You found treasure!\n**Loot**: {berries} Berries" + (f"\n**Relics**: {', '.join(items)}" if items else "") + "\n══════"
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Island Conquered!",
                    description="🌊 You’ve explored an island! Check your loot.\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
            except:
                pass
        else:
            loss = random.randint(10, 30)
            economy[user_id]["berries"] = max(0, economy[user_id]["berries"] - loss)
            embed.description = f"🌊 Danger struck! You lost {loss} Berries.\n══════"
            await ctx.send(embed=embed)
        
        embed.set_footer(text="One Piece Adventure")
        save_economy(economy)
    except Exception as e:
        print(f"Error in exploreisland for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))

@bot.command(name="fish")
@commands.cooldown(1, 60, commands.BucketType.user)
async def fish(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.80
        if economy[user_id]["active_race"] == "Skypian":
            success_chance += 0.10
        
        embed = nextcord.Embed(
            title="🏴‍☠️ Fishing Trip",
            description="🌊 You cast your line into the sea!\n══════",
            color=0x2A4B7C
        )
        if random.random() < success_chance:
            berries = random.randint(10, 40)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            
            items = []
            item_chance = 0.03
            if economy[user_id]["active_race"] == "Shark":
                item_chance += 0.15
            if random.random() < item_chance:
                items.append("Pearl")
                economy[user_id]["inventory"].append("Pearl")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"]["fish_caught"] += 1
            
            embed.description = f"🌊 Nice catch!\n**Loot**: {berries} Berries" + (f"\n**Treasures**: {', '.join(items)}" if items else "") + "\n══════"
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Fish Hooked!",
                    description="🌊 You’ve reeled in a prize! Check your loot.\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
            except:
                pass
        else:
            embed.description = f"🌊 Nothing bit! Try again.\n══════"
            await ctx.send(embed=embed)
        
        embed.set_footer(text="One Piece Adventure")
        save_economy(economy)
    except Exception as e:
        print(f"Error in fish for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))

@bot.command(name="raid")
@commands.cooldown(1, 3600, commands.BucketType.guild)
async def raid(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        participants = {ctx.author.id}
        embed = nextcord.Embed(
            title="🏴‍☠️ Fortress Raid",
            description=f"🌊 {ctx.author.mention} calls for a raid. Max 5 pirates!\nType 'join' within 60 seconds.\n══════",
            color=0x2A4B7C
        )
        embed.set_footer(text="One Piece Adventure")
        await ctx.send(embed=embed)
        
        def check(m):
            return m.channel.id == ctx.channel.id and m.content.lower() == "join" and m.author.id not in participants
        
        try:
            while len(participants) < 5:
                message = await bot.wait_for("message", check=check, timeout=60 - (len(participants) * 10))
                participants.add(message.author.id)
                economy = initialize_user(economy, str(message.author.id))
                embed.description = f"🌊 {ctx.author.mention} leads the raid. {len(participants)}/5 pirates!\nType 'join' to participate.\n══════"
                await ctx.send(embed=embed)
        
        except asyncio.TimeoutError:
            pass
        
        if len(participants) < 2:
            await ctx.send(embed=nextcord.Embed(
                title="🏴‍☠️ Raid Canceled",
                description="🌊 Not enough pirates! Need at least 2.\n══════",
                color=0x2A4B7C
            ).set_footer(text="One Piece Adventure"))
            return
        
        success_chance = 0.60 + 0.05 * (len(participants) - 1)
        for pid in participants:
            if economy[str(pid)]["active_race"] == "Mink":
                success_chance += 0.10
                break
        
        embed = nextcord.Embed(
            title="🏴‍☠️ Raid Begins",
            description=f"🌊 {len(participants)} pirates storm the fortress!\n══════",
            color=0x2A4B7C
        )
        if random.random() < success_chance:
            for pid in participants:
                berries = random.randint(100, 200)
                if economy[str(pid)]["active_race"] == "Human":
                    berries = int(berries * 1.10)
                armament_level = economy[str(pid)]["haki"]["armament"]["level"]
                berries = int(berries * (1 + 0.10 * armament_level))
                
                items = []
                item_chance = 0.10
                if economy[str(pid)]["active_race"] == "Cyborg":
                    item_chance += 0.10
                if random.random() < item_chance:
                    items.append("Fortress Key")
                    economy[str(pid)]["inventory"].append("Fortress Key")
                
                economy[str(pid)]["berries"] += berries
                economy[str(pid)]["achievements"]["berries_earned"] += berries
                economy[str(pid)]["achievements"]["raids_completed"] += 1
            
            embed.description = f"🌊 Victory! Each pirate gains {berries} Berries" + (f" and {', '.join(items)}" if items else "") + ".\n══════"
            await ctx.send(embed=embed)
            for pid in participants:
                try:
                    member = ctx.guild.get_member(int(pid))
                    await member.send(embed=nextcord.Embed(
                        title="🏴‍☠️ Fortress Conquered!",
                        description="🌊 The raid succeeded! Check your loot.\n══════",
                        color=0x2A4B7C
                    ).set_footer(text="One Piece Adventure"))
                except:
                    pass
        else:
            embed.description = f"🌊 The marines repelled you! Try again.\n══════"
            await ctx.send(embed=embed)
        
        embed.set_footer(text="One Piece Adventure")
        save_economy(economy)
    except Exception as e:
        print(f"Error in raid for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))


@bot.command(name="navalbattle")
@commands.cooldown(1, 1200, commands.BucketType.user)
async def naval_battle(ctx):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        success_chance = 0.55
        if economy[user_id]["active_race"] == "Shark":
            success_chance += 0.15
        observation_level = economy[user_id]["haki"]["observation"]["level"]
        success_chance += 0.05 * observation_level
        if economy[user_id]["haki"]["active_buff"] and economy[user_id]["haki"]["active_buff"]["type"] == "observation" and economy[user_id]["haki"]["active_buff"]["expires"] > time.time():
            success_chance += 0.10 * observation_level
        
        embed = nextcord.Embed(
            title="🏴‍☠️ Naval Battle",
            description="🌊 Cannons roar as you engage an enemy ship!\n══════",
            color=0x2A4B7C
        )
        if random.random() < success_chance:
            berries = random.randint(90, 180)
            if economy[user_id]["active_race"] == "Human":
                berries = int(berries * 1.10)
            armament_level = economy[user_id]["haki"]["armament"]["level"]
            berries = int(berries * (1 + 0.10 * armament_level))
            
            items = []
            item_chance = 0.06
            if economy[user_id]["active_race"] == "Cyborg":
                item_chance += 0.10
            if random.random() < item_chance:
                items.append("Cannonball Crate")
                economy[user_id]["inventory"].append("Cannonball Crate")
            
            economy[user_id]["berries"] += berries
            economy[user_id]["achievements"]["berries_earned"] += berries
            economy[user_id]["achievements"]["ships_sunk"] += 1
            
            embed.description = f"🌊 You sank the enemy ship!\n**Loot**: {berries} Berries" + (f"\n**Salvage**: {', '.join(items)}" if items else "") + "\n══════"
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Ship Sunk!",
                    description="🌊 You’ve claimed victory at sea! Check your loot.\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
            except:
                pass
        else:
            embed.description = f"🌊 The enemy outgunned you! Retreat and try again.\n══════"
            await ctx.send(embed=embed)
        
        embed.set_footer(text="One Piece Adventure")
        save_economy(economy)
    except Exception as e:
        print(f"Error in navalbattle for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))        


@bot.command(name="formcrew")
@commands.cooldown(1, 86400, commands.BucketType.user)
async def form_crew(ctx, crew_name: str = None):
    try:
        economy = load_economy()
        user_id = str(ctx.author.id)
        economy = initialize_user(economy, user_id)
        
        if crew_name:  # Create a crew
            if "crew" in economy[user_id]:
                await ctx.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Crew Conflict",
                    description="🌊 You’re already in a crew, pirate!\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
                return
            
            economy[user_id]["crew"] = {"name": crew_name, "members": [user_id], "leader": user_id}
            economy[user_id]["achievements"]["crews_joined"] += 1
            
            embed = nextcord.Embed(
                title="🏴‍☠️ Crew Formed",
                description=f"🌊 {ctx.author.mention} founded the **{crew_name}** crew!\nUse `?formcrew join {crew_name}` to recruit others.\n══════",
                color=0x2A4B7C
            )
            await ctx.send(embed=embed)
            try:
                await ctx.author.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Captain’s Log",
                    description=f"🌊 You’re now the leader of **{crew_name}**!\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
            except:
                pass
        
        else:  # Join a crew
            if "crew" in economy[user_id]:
                await ctx.send(embed=nextcord.Embed(
                    title="🏴‍☠️ Crew Conflict",
                    description="🌊 You’re already in a crew, pirate!\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
                return
            
            crew_name = ctx.message.content.split("join ", 1)[1] if "join" in ctx.message.content.lower() else None
            if not crew_name:
                await ctx.send(embed=nextcord.Embed(
                    title="🏴‍☠️ No Crew Specified",
                    description="🌊 Use `?formcrew join <crew_name>` to join a crew!\n══════",
                    color=0x2A4B7C
                ).set_footer(text="One Piece Adventure"))
                return
            
            for uid, data in economy.items():
                if data.get("crew", {}).get("name") == crew_name and len(data["crew"]["members"]) < 10:
                    economy[user_id]["crew"] = {"name": crew_name, "members": data["crew"]["members"] + [user_id], "leader": data["crew"]["leader"]}
                    economy[uid]["crew"]["members"].append(user_id)
                    economy[user_id]["achievements"]["crews_joined"] += 1
                    
                    embed = nextcord.Embed(
                        title="🏴‍☠️ Crew Joined",
                        description=f"🌊 {ctx.author.mention} joined the **{crew_name}** crew!\nEnjoy a +5% Berry bonus.\n══════",
                        color=0x2A4B7C
                    )
                    await ctx.send(embed=embed)
                    try:
                        await ctx.author.send(embed=nextcord.Embed(
                            title="🏴‍☠️ Welcome Aboard!",
                            description=f"🌊 You’re now part of **{crew_name}**!\n══════",
                            color=0x2A4B7C
                        ).set_footer(text="One Piece Adventure"))
                    except:
                        pass
                    save_economy(economy)
                    return
            
            await ctx.send(embed=nextcord.Embed(
                title="🏴‍☠️ Crew Not Found",
                description=f"🌊 No crew named **{crew_name}** exists or it’s full!\n══════",
                color=0x2A4B7C
            ).set_footer(text="One Piece Adventure"))
            return
        
        if economy[user_id]["active_race"] == "Mink":
            ctx.command.reset_cooldown(ctx)
        
        save_economy(economy)
    
    except Exception as e:
        print(f"Error in formcrew for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="🏴‍☠️ Error",
            description="🌊 Storm at sea, pirate! Try again.\n══════",
            color=0x2A4B7C
        ).set_footer(text="One Piece Adventure"))







@bot.command(name="profile")
async def profile(ctx, member: nextcord.Member = None):
    try:
        member = member or ctx.author
        economy = load_economy()
        user_id = str(member.id)
        economy = initialize_user(economy, user_id)
        
        embed = nextcord.Embed(
            title=f"🌴 {member.display_name}'s Profile",
            color=0xFF0000
        )
        embed.add_field(
            name=" Economy",
            value=f"**Berries**: {economy[user_id]['berries']}\n**Bank**: {economy[user_id]['bank']}",
            inline=True
        )
        embed.add_field(
            name="🧬 Race",
            value=f"**Active**: {economy[user_id]['active_race'] or 'None'}\n**Owned**: {', '.join(economy[user_id]['races_owned']) or 'None'}",
            inline=True
        )
        embed.add_field(
            name="🍎 Fruits",
            value=f"**Owned**: {', '.join(economy[user_id].get('fruits', [])) or 'None'}",
            inline=True
        )
        embed.add_field(
            name="🌀 Haki",
            value=(
                f"**Observation**: Level {economy[user_id]['haki']['observation']['level']} ({economy[user_id]['haki']['observation']['exp']}/100 EXP)\n"
                f"**Armament**: Level {economy[user_id]['haki']['armament']['level']} ({economy[user_id]['haki']['armament']['exp']}/100 EXP)\n"
                f"**Active Buff**: {economy[user_id]['haki']['active_buff']['type'].title() if economy[user_id]['haki']['active_buff'] and economy[user_id]['haki']['active_buff']['expires'] > time.time() else 'None'}"
            ),
            inline=False
        )
        embed.add_field(
            name="🎒 Inventory",
            value=", ".join(economy[user_id]["inventory"]) or "Empty",
            inline=False
        )
        embed.add_field(
            name="🏴‍☠️ Crew",
            value=f"**Crew**: {economy[user_id].get('crew', {}).get('name', 'None')}",
            inline=False
        )
        embed.add_field(
            name="🏆 Achievements",
            value=(
                f"**Bosses Killed**: {economy[user_id]['achievements']['bosses_killed']}\n"
                f"**Pirates Killed**: {economy[user_id]['achievements'].get('pirates_killed', 0)}\n"
                f"**Marines Killed**: {economy[user_id]['achievements'].get('marines_killed', 0)}\n"
                f"**Sea Beasts Killed**: {economy[user_id]['achievements'].get('seabeasts_killed', 0)}\n"
                f"**Islands Explored**: {economy[user_id]['achievements'].get('islands_explored', 0)}\n"
                f"**Trades Completed**: {economy[user_id]['achievements'].get('trades_completed', 0)}\n"
                f"**Bounties Hunted**: {economy[user_id]['achievements'].get('bounties_hunted', 0)}\n"
                f"**Fish Caught**: {economy[user_id]['achievements'].get('fish_caught', 0)}\n"
                f"**Raids Completed**: {economy[user_id]['achievements'].get('raids_completed', 0)}\n"
                f"**Treasures Found**: {economy[user_id]['achievements'].get('treasures_found', 0)}\n"
                f"**Ships Sunk**: {economy[user_id]['achievements'].get('ships_sunk', 0)}\n"
                f"**Riddles Solved**: {economy[user_id]['achievements'].get('riddles_solved', 0)}\n"
                f"**Arenas Won**: {economy[user_id]['achievements'].get('arenas_won', 0)}\n"
                f"**Crews Joined**: {economy[user_id]['achievements'].get('crews_joined', 0)}\n"
                f"**Successful Steals**: {economy[user_id]['achievements']['steals_succeeded']}\n"
                f"**Daily Streak**: {economy[user_id]['achievements']['daily_streak']} days\n"
                f"**Berries Earned**: {economy[user_id]['achievements']['berries_earned']}"
            ),
            inline=False
        )
        embed.set_footer(text="Blox Fruits Bot")
        await ctx.send(embed=embed)
        
        save_economy(economy)
    except Exception as e:
        print(f"Error in profile for user {user_id}: {e}")
        await ctx.send(embed=nextcord.Embed(
            title="❌ Error",
            description="Failed to load profile! Try again later.",
            color=0xFF0000
        ))













@bot.slash_command(description="Ask the AI about Blox Fruits or anything")
@commands.cooldown(1, 15, commands.BucketType.user)
async def askai(interaction: Interaction, question: str = SlashOption(description="Your question for the AI")):
    await interaction.response.defer()
    

    API_KEY = ""
    
   
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "http://test-hub.kys.gay/api/gemini-pro",
                params={"prompt": question, "key": API_KEY}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data.get("response", "Sorry, no answer found. Try again!")
                else:
                    answer = "Couldn't reach the AI. Try later!"
        except Exception as e:
            answer = f"Error: {str(e)}. Try again!"
    
    
    await interaction.followup.send(answer)






@bot.slash_command(name="generate_image", description="Generates an image using the API.")
async def generate_image_command(interaction: Interaction, prompt: str = SlashOption(description="The prompt for the image generation")):
    """Slash command to generate an image without a loading embed."""
    await interaction.response.defer()  

    params = {"prompt": prompt, "key": IMAGE_API_KEY}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(IMAGE_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data.get("image")
                    if image_url:
                        embed = Embed(title="✨ Generated Image ✨", color=nextcord.Color.blurple())
                        embed.set_image(url=image_url)
                        embed.set_footer(text=f"Prompt: {prompt}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
                        await interaction.followup.send(embed=embed) 
                    else:
                        await interaction.followup.send(embed=Embed(title="⚠️ Error", description="The API did not return an image URL.", color=nextcord.Color.red()))
                else:
                    await interaction.followup.send(embed=Embed(title="⚠️ API Error", description=f"The API returned an error: {response.status}", color=nextcord.Color.red()))
        except aiohttp.ClientError as e:
            await interaction.followup.send(embed=Embed(title="⚠️ Connection Error", description=f"There was an error connecting to the API: {e}", color=nextcord.Color.red()))







# Play queues per server
audio_queues = {}
is_playing_in = {}
current_audio_info_in = {}
voice_clients = {}

ydl_opts_advanced_nobuttons = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'include_info_json': True,
}

ffmpeg_options_advanced_nobuttons = {
    'options': '-vn',
}

async def get_audio_info_advanced_nobuttons(query):
    with yt_dlp.YoutubeDL(ydl_opts_advanced_nobuttons) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if 'entries' in info:
                return info['entries'][0]
            return None
        except Exception as e:
            print(f"Error with yt-dlp: {e}")
            return None

async def play_next_audio_advanced_nobuttons(guild_id):
    if guild_id in audio_queues and audio_queues[guild_id]:
        global voice_clients, is_playing_in, current_audio_info_in
        next_audio = audio_queues[guild_id].popleft()
        voice_client = bot.get_guild(guild_id).voice_client

        if voice_client and voice_client.is_connected() and voice_client.channel:
            try:
                source = nextcord.FFmpegPCMAudio(next_audio['url'], **ffmpeg_options_advanced_nobuttons)
                voice_client.play(source, after=lambda e: song_finished_advanced_nobuttons(guild_id))
                is_playing_in[guild_id] = True
                current_audio_info_in[guild_id] = next_audio
                embed = Embed(title="🎶 Now Playing:", description=f"[{next_audio['title']}]({next_audio['webpage_url'] if 'webpage_url' in next_audio else next_audio['audio_url']})", color=nextcord.Color.green())
                if 'thumbnail' in next_audio:
                    embed.set_thumbnail(url=next_audio['thumbnail'])
                if 'duration' in next_audio:
                    minutes, seconds = divmod(next_audio['duration'], 60)
                    embed.add_field(name="Duration:", value=f"{int(minutes)}:{int(seconds):02d}", inline=True)
                if 'uploader' in next_audio:
                    embed.add_field(name="Uploaded by:", value=next_audio['uploader'], inline=True)
                await voice_client.channel.send(embed=embed)
            except Exception as e:
                print(f"Error playing audio: {e}")
                is_playing_in[guild_id] = False
                current_audio_info_in[guild_id] = None
                if voice_client and voice_client.channel:
                    await voice_client.channel.send(f"⚠️ Error playing audio: {e}")
        else:
            is_playing_in[guild_id] = False
            current_audio_info_in[guild_id] = None
            if voice_client and voice_client.channel:
                await voice_client.channel.send("⚠️ Not connected to a voice channel.")
    else:
        is_playing_in[guild_id] = False
        current_audio_info_in[guild_id] = None
        voice_client = bot.get_guild(guild_id).voice_client
        if voice_client and voice_client.is_connected() and voice_client.channel:
            await voice_client.channel.send("⏹️ Queue finished.")

async def song_finished_advanced_nobuttons(guild_id):
    if guild_id in is_playing_in and not is_playing_in[guild_id]:
        if guild_id in audio_queues and audio_queues[guild_id]:
            await play_next_audio_advanced_nobuttons(guild_id)
        else:
            voice_client = bot.get_guild(guild_id).voice_client
            if voice_client and voice_client.is_connected() and voice_client.channel:
                await voice_client.channel.send("🎵 Queue finished.")

@bot.slash_command(name="play", description="Plays music by name or link.")
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def play_command_advanced_nobuttons(interaction: Interaction, query: str = SlashOption(description="Song name or link.")):
    await interaction.response.defer()

    voice_channel = interaction.user.voice.channel if interaction.user and interaction.user.voice else None
    if not voice_channel:
        await interaction.followup.send("⚠️ You must be in a voice channel.", ephemeral=True)
        return

    audio_info = await get_audio_info_advanced_nobuttons(query)
    if audio_info:
        embed = Embed(title="🎶 Found Song:", description=f"[{audio_info['title']}]({audio_info['webpage_url'] if 'webpage_url' in audio_info else audio_info['audio_url']})", color=nextcord.Color.blue())
        if 'thumbnail' in audio_info:
            embed.set_thumbnail(url=audio_info['thumbnail'])
        await interaction.followup.send(embed=embed)

        guild_id = interaction.guild_id
        if guild_id not in audio_queues:
            audio_queues[guild_id] = deque()
        audio_queues[guild_id].append(audio_info)
        await interaction.followup.send(f"✅ Added to queue. Queue length: {len(audio_queues[guild_id])}")

        voice_client = await voice_channel.connect()
        voice_clients[guild_id] = voice_client  # Store the voice client

        if not is_playing_in.get(guild_id):
            await play_next_audio_advanced_nobuttons(guild_id)
        elif not voice_client.is_playing():
            await play_next_audio_advanced_nobuttons(guild_id)
    else:
        await interaction.followup.send("❌ No songs found.", ephemeral=True)

@bot.slash_command(name="pause", description="Pauses the currently playing song.")
@commands.guild_only()
async def pause_command_advanced_nobuttons(interaction: Interaction):
    guild_id = interaction.guild_id
    voice_client = bot.get_guild(guild_id).voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Paused.")
    else:
        await interaction.response.send_message("⚠️ Nothing is currently playing.", ephemeral=True)

@bot.slash_command(name="resume", description="Resumes the currently paused song.")
@commands.guild_only()
async def resume_command_advanced_nobuttons(interaction: Interaction):
    guild_id = interaction.guild_id
    voice_client = bot.get_guild(guild_id).voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Resumed.")
    else:
        await interaction.response.send_message("⚠️ Nothing is currently paused.", ephemeral=True)

@bot.slash_command(name="skip", description="Skips the currently playing song.")
@commands.guild_only()
async def skip_command_advanced_nobuttons(interaction: Interaction):
    guild_id = interaction.guild_id
    voice_client = bot.get_guild(guild_id).voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped.")
    else:
        await interaction.response.send_message("⚠️ Nothing is currently playing.", ephemeral=True)

@bot.slash_command(name="stop", description="Stops the music and clears the queue.")
@commands.guild_only()
async def stop_command_advanced_nobuttons(interaction: Interaction):
    guild_id = interaction.guild_id
    voice_client = bot.get_guild(guild_id).voice_client
    if voice_client:
        await voice_client.disconnect()
        if guild_id in audio_queues:
            del audio_queues[guild_id]
        is_playing_in[guild_id] = False
        current_audio_info_in[guild_id] = None
        await interaction.response.send_message("⏹️ Stopped and disconnected.")
    else:
        await interaction.response.send_message("⚠️ Not connected to a voice channel.", ephemeral=True)

@bot.slash_command(name="queue", description="Displays the current music queue.")
@commands.guild_only()
async def queue_command_advanced_nobuttons(interaction: Interaction):
    guild_id = interaction.guild_id
    if guild_id in audio_queues and audio_queues[guild_id]:
        queue_list = [f"{i+1}. {item['title']}" for i, item in enumerate(audio_queues[guild_id])]
        queue_string = "\n".join(queue_list)
        embed = Embed(title="🎵 Music Queue", description=queue_string, color=nextcord.Color.blurple())
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("🎶 The queue is currently empty.", ephemeral=True)



























@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if not spawn_random_boss.is_running():
        spawn_random_boss.start()





@bot.event
async def on_application_command_error(interaction: Interaction, error):
    if hasattr(interaction, 'application_command') and interaction.application_command:
        await log_error(f"Command error in {interaction.application_command.name}: {str(error)}", interaction.guild_id)
    else:
        await log_error(f"Command error: {str(error)}", interaction.guild_id) # Fallback in case application_command is None
    # You might want to add more specific error handling here based on the 'error' type
    await interaction.send(f"An error occurred while processing your command. Please try again later.", ephemeral=True)

async def log_error(message: str, guild_id: int | None = None):
    # Your existing error logging logic here
    print(f"ERROR: {message} (Guild ID: {guild_id})")



if __name__ == "__main__":
    bot.run(BOT_TOKEN)
