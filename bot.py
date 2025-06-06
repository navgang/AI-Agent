import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Setup OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Setup Discord bot
intents = discord.Intents.default()
intents.message_content = True  # Required for reading messages in 2.x

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}!")

# 🔒 Private summary command (ephemeral)
@tree.command(name="summarize", description="Summarize the last 50 messages with action items (private)")
async def summarize(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True, thinking=True)

    # Fetch last 50 messages
    messages = []
    async for msg in interaction.channel.history(limit=50):
        if msg.content:
            messages.append(msg.content)
    messages_text = "\n".join(reversed(messages))

    prompt = f"""
    You are an AI meeting assistant. Your task is to:
    1️⃣ Provide a concise 3-4 sentence summary of the following conversation.
    2️⃣ Identify any action items, tasks, or next steps that are mentioned or implied.

    Conversation:
    {messages_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You’re a helpful meeting summarizer and action item tracker."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
        await interaction.followup.send(f"**Summary & Action Items:**\n{answer}", ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"Oops! Something went wrong:\n```{e}```", ephemeral=True)

# 🌟 Public summary command (visible to everyone)
@tree.command(name="summarize_publicly", description="Summarize the last 50 messages with action items (public)")
async def summarize_publicly(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)  # No ephemeral=True here!

    # Fetch last 50 messages
    messages = []
    async for msg in interaction.channel.history(limit=50):
        if msg.content:
            messages.append(msg.content)
    messages_text = "\n".join(reversed(messages))

    prompt = f"""
    You are an AI meeting assistant. Your task is to:
    1️⃣ Provide a concise 3-4 sentence summary of the following conversation.
    2️⃣ Identify any action items, tasks, or next steps that are mentioned or implied.

    Conversation:
    {messages_text}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You’re a helpful meeting summarizer and action item tracker."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content.strip()
        await interaction.followup.send(f"**Summary & Action Items:**\n{answer}")

    except Exception as e:
        await interaction.followup.send(f"Oops! Something went wrong:\n```{e}```")

bot.run(DISCORD_TOKEN)