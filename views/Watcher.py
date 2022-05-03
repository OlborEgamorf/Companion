intent=discord.Intents(messages=True,guilds=True,members=True,bans=False,emojis=True,integrations=False,webhooks=False,invites=False,voice_states=True,reactions=True,dm_messages=False,dm_reactions=False,dm_typing=False)
bot=commands.Bot(command_prefix=(commands.when_mentioned_or('OT!',"ot!","Ot!","oT!")), case_insensitive=True, intents=intent,chunk_guilds_at_startup=True)

bot.remove_command("help")

@bot.listen()
async def on_guild_join(guild):
    pass

@bot.listen()
async def on_guild_remove(guild):
    pass
@bot.listen()
async def on_member_remove(member):
    pass
@bot.listen()
async def on_member_join(member):
    pass
@bot.listen()
async def on_guild_channel_create(channel):
    pass
@bot.listen()
async def on_guild_channel_delete(channel):
    pass

@bot.listen()
async def on_member_update(before, after):
    pass
@bot.listen()
async def on_guild_update(before, after):
    pass
@bot.listen()
async def on_guild_role_create(role):
    pass
@bot.listen()
async def on_guild_role_delete(role):
    pass
@bot.listen()
async def on_guild_role_update(before, after):
    pass
@bot.listen()
async def on_guild_emojis_update(guild, before, after):
    pass