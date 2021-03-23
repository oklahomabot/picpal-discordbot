discord-image-bot
Discord image manipulation bot

This repo is intended to be used by copying the (images folder AND the images.py file) located in this repl's 'cogs' folder into your bot's "COGS" folder

New "fun images" can be created by just putting a new image into the sub-folder 'masters.' New images will be detected when the bot starts and can be customized using the bot's editing functions. Data is stored in data folder in images.db.

This repl not intended to run "as is," but if you want to use by itself, create a .env file in top level with your discord token as 'dTOKEN', Pixabay.com API token as PIXABAY_API_KEY and BOT owner's discord user id as OWNERid

NOTE : "fun images" filenames become commands in discord. There will be a conflict if you have the same name for an image in the 'masters' folder as another command ex) slap, purge ... and it will have to be resolved by renaming an image or renaming the conflicting command elsewhere in your bot.