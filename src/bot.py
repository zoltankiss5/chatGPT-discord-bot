import os
import openai
import asyncio
import discord
from random import randrange
from src.aclient import client
from discord import app_commands
from src import log, responses
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

logger = log.setup_logger(__name__)
current_persona = "standard"

db = AsyncIOMotorClient(os.getenv("MONGO_CONN_URI"), server_api=ServerApi('1'))

def run_discord_bot():
    @client.event
    async def on_ready():
        await client.send_start_prompt()
        await client.tree.sync()
        asyncio.create_task(client.process_messages())
        logger.info(f'{client.user} is now running!')


    @client.tree.command(name="chat", description="Have a chat with ChatGPT")
    async def chat(interaction: discord.Interaction, *, message: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.enqueue_message(interaction, message)

    @client.tree.command(name="startsession", description="Start working session with tickets")
    async def startsession(interaction: discord.Interaction):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info("Interaction.channel is: " + str(interaction.channel))
        await client.enqueue_message(interaction, f"{''.join(open('./prompts/startsession.txt', 'r').readlines()).strip()} {(await db['code-games']['test'].find_one({}))['ai_summary']}")
        logger.info("Working session with tickets started")

    @client.tree.command(name="ticket", description="Add new ticket")
    async def ticket(interaction: discord.Interaction, *, ticketnumber: str, ticketdescription: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        await client.enqueue_message(interaction, "Initialize " + ticketnumber + ":" + ticketdescription)
        logger.info("New ticket initialized")

    @client.tree.command(name="ticketlog", description="Add new log entry to ticket")
    async def ticketlog(interaction: discord.Interaction, *, ticketnumber: str, ticketlog: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        await client.enqueue_message(interaction, "Ticket is " + ticketnumber + ". Add this log entry to this ticket: " + ticketlog)
        logger.info("New ticket initialized")

    @client.tree.command(name="summarize", description="Summarize a ticket")
    async def summarize(interaction: discord.Interaction, *, ticket_id: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        message = f"summarize {ticket_id}"

        logger.info(
            f"\x1b[31m{username}\x1b[0m : /chat [{message}] in ({channel})")
        await client.enqueue_message(interaction, message)


    @client.tree.command(name="selectrole", description="Select role for accessing the tickets")
    async def selectrole(interaction: discord.Interaction, *, roleselection: str):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        if roleselection.startswith("team"):
            roleprompt = ''.join(open("./prompts/team.txt", "r").readlines()).strip()
        elif roleselection.startswith("lead"):
            roleprompt = ''.join(open("./prompts/lead.txt", "r").readlines()).strip()
        elif roleselection.startswith("customer"):
            roleprompt = ''.join(open("./prompts/customer.txt", "r").readlines()).strip()
        await client.enqueue_message(interaction, roleprompt)
        logger.info("Role selected for session is {roleselection}")

    @client.tree.command(name="stopsession", description="Stop working session with tickets")
    async def stopsession(interaction: discord.Interaction):
        if client.is_replying_all == "True":
            await interaction.response.defer(ephemeral=False)
            await interaction.followup.send(
                "> **WARN: You already on replyAll mode. If you want to use the Slash Command, switch to normal mode by using `/replyall` again**")
            logger.warning("\x1b[31mYou already on replyAll mode, can't use slash command!\x1b[0m")
            return
        if interaction.user == client.user:
            return
        username = str(interaction.user)
        channel = str(interaction.channel)
        logger.info("Working session with tickets stopped")
        await client.enqueue_message(interaction, f"summary")

    @client.tree.command(name="private", description="Toggle private access")
    async def private(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if not client.isPrivate:
            client.isPrivate = not client.isPrivate
            logger.warning("\x1b[31mSwitch to private mode\x1b[0m")
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent via private reply. If you want to switch back to public mode, use `/public`**")
        else:
            logger.info("You already on private mode!")
            await interaction.followup.send(
                "> **WARN: You already on private mode. If you want to switch to public mode, use `/public`**")

    @client.tree.command(name="public", description="Toggle public access")
    async def public(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.isPrivate:
            client.isPrivate = not client.isPrivate
            await interaction.followup.send(
                "> **INFO: Next, the response will be sent to the channel directly. If you want to switch back to private mode, use `/private`**")
            logger.warning("\x1b[31mSwitch to public mode\x1b[0m")
        else:
            await interaction.followup.send(
                "> **WARN: You already on public mode. If you want to switch to private mode, use `/private`**")
            logger.info("You already on public mode!")


    @client.tree.command(name="replyall", description="Toggle replyAll access")
    async def replyall(interaction: discord.Interaction):
        client.replying_all_discord_channel_id = str(interaction.channel_id)
        await interaction.response.defer(ephemeral=False)
        if client.is_replying_all == "True":
            client.is_replying_all = "False"
            await interaction.followup.send(
                "> **INFO: Next, the bot will response to the Slash Command. If you want to switch back to replyAll mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to normal mode\x1b[0m")
        elif client.is_replying_all == "False":
            client.is_replying_all = "True"
            await interaction.followup.send(
                "> **INFO: Next, the bot will disable Slash Command and responding to all message in this channel only. If you want to switch back to normal mode, use `/replyAll` again**")
            logger.warning("\x1b[31mSwitch to replyAll mode\x1b[0m")


    @client.tree.command(name="chat-model", description="Switch different chat model")
    @app_commands.choices(choices=[
        app_commands.Choice(name="Official GPT-3.5", value="OFFICIAL"),
        app_commands.Choice(name="Ofiicial GPT-4.0", value="OFFICIAL-GPT4"),
    ])

    async def chat_model(interaction: discord.Interaction, choices: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        original_chat_model = client.chat_model
        original_openAI_gpt_engine = client.openAI_gpt_engine

        try:
            if choices.value == "OFFICIAL":
                client.openAI_gpt_engine = "gpt-3.5-turbo"
                client.chat_model = "OFFICIAL"
            elif choices.value == "OFFICIAL-GPT4":
                client.openAI_gpt_engine = "gpt-4"
                client.chat_model = "OFFICIAL"
            else:
                raise ValueError("Invalid choice")

            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **INFO: You are now in {client.chat_model} model.**\n")
            logger.warning(f"\x1b[31mSwitch to {client.chat_model} model\x1b[0m")

        except Exception as e:
            client.chat_model = original_chat_model
            client.openAI_gpt_engine = original_openAI_gpt_engine
            client.chatbot = client.get_chatbot_model()
            await interaction.followup.send(f"> **ERROR: Error while switching to the {choices.value} model, check that you've filled in the related fields in `.env`.**\n")
            logger.exception(f"Error while switching to the {choices.value} model: {e}")


    @client.tree.command(name="reset", description="Complete reset conversation history")
    async def reset(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        if client.chat_model == "OFFICIAL":
            client.chatbot = client.get_chatbot_model()
        elif client.chat_model == "UNOFFICIAL":
            client.chatbot.reset_chat()
            await client.send_start_prompt()
        elif client.chat_model == "Bard":
            client.chatbot = client.get_chatbot_model()
            await client.send_start_prompt()
        elif client.chat_model == "Bing":
            await client.chatbot.reset()
        await interaction.followup.send("> **INFO: I have forgotten everything.**")
        current_persona = "standard"
        logger.warning(
            f"\x1b[31m{client.chat_model} bot has been successfully reset\x1b[0m")

    @client.event
    async def on_message(message):
        if client.is_replying_all == "True":
            if message.author == client.user:
                return
            if client.replying_all_discord_channel_id:
                if message.channel.id == int(client.replying_all_discord_channel_id):
                    username = str(message.author)
                    user_message = str(message.content)
                    channel = str(message.channel)
                    logger.info(f"\x1b[31m{username}\x1b[0m : '{user_message}' ({channel})")
                    await client.enqueue_message(message, user_message)
            else:
                logger.exception("replying_all_discord_channel_id not found, please use the commnad `/replyall` again.")

    TOKEN = os.getenv("DISCORD_BOT_TOKEN")

    client.run(TOKEN)
