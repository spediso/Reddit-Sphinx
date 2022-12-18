# Reddit-Sphinx

## Introduction
This script is a Reddit bot that uses the OpenAI API to generate responses to comments and submissions on Reddit. The bot will authenticate with both Reddit and OpenAI, and then ask the user if they want to reply to any comments or submissions that it comes across. If the user selects yes, the bot will generate a response using OpenAI and post it as a reply on Reddit.

## Requirements
- Python 3.7 or later
- `praw` library: `pip install praw`
- `openai` library: `pip install openai`
- `rich` library: `pip install rich`
- `tqdm` library: `pip install tqdm`
- `dotenv` library: `pip install python-dotenv`

## Setup
1. Register for a Reddit account and create a Reddit app at https://www.reddit.com/prefs/apps
2. Obtain your Reddit app's client ID and client secret, and set them as the values for the `PRAW_CLIENT_ID` and `PRAW_CLIENT_SECRET` environment variables, respectively.
3. Set the value for the `PRAW_USER_AGENT` environment variable to a string that describes your Reddit app.
4. Set the value for the `PRAW_USERNAME` environment variable to your Reddit username.
5. Set the value for the `PRAW_PASSWORD` environment variable to your Reddit password.
6. Register for an OpenAI API key at https://beta.openai.com/signup/
7. Set the value for the `OPENAI_API_KEY` environment variable to your OpenAI API key.

## Usage
1. Run the script using `python script.py`
2. The bot will authenticate with Reddit and OpenAI, and will then begin searching for comments and submissions to reply to. When it finds a comment or submission, it will ask the user if they want to reply.
3. If the user selects yes, the bot will generate a response using OpenAI and post it as a reply on Reddit.
4. The bot will continue running until it is manually stopped.

## Logging
The bot logs all actions to the `bot.log` file, including the time at which each action was taken, the name of the action, and any relevant messages. The log file is located in the same directory as the script.
