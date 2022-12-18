import praw
from praw.models import Comment
import openai
import os
import time
import datetime
import logging
from rich.pretty import pprint
from rich.console import Console
from rich.prompt import Prompt
from tqdm import tqdm
import os
import sys
from dotenv import load_dotenv

# load environment variables
load_dotenv()

# set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('bot.log', encoding='utf-8')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)
# set up console
console = Console()
# add a log header
logger.info('~'*50)
logger.info("Bot started")
logger.info('~'*50)

# authenticate with reddit
reddit = praw.Reddit(client_id=os.environ.get("PRAW_CLIENT_ID"),
                     client_secret=os.environ.get("PRAW_CLIENT_SECRET"),
                     user_agent=os.environ.get("PRAW_USER_AGENT"),
                     username=os.environ.get("PRAW_USERNAME"),
                     password=os.environ.get("PRAW_PASSWORD"))
logger.info("Reddit authenticated")
# authenticate with openai
openai.api_key = os.getenv("OPENAI_API_KEY")
logger.info("OpenAI authenticated")

# start time
start_time = time.time()
# initial prompts
# clear the console
os.system("cls" if os.name == "nt" else "clear")
# Ask user for subreddit
subreddit_name = Prompt.ask(
    "[green]What subreddit do you want to monitor?[/green]", default="all")
# clear the console
os.system("cls" if os.name == "nt" else "clear")
# Ask user for keyword
keyword = Prompt.ask(
    "[green]What keyword do you want to monitor?[/green]", default="kangaroo")
# clear the console
os.system("cls" if os.name == "nt" else "clear")

# set of ids of comments that have been replied to updated with tqdm
commented_ids = set()
logger.info("Commented_ids set created")
# set of ids of seen comments updated with tqdm
seen_ids = set()
logger.info("Seen_ids set created")

# Get the bot's user object
bot_user = reddit.user.me()
# Get a list of the bot's past comments
bot_comments = list(bot_user.comments.new())
# Get a list of the bot's past submissions
bot_submissions = list(bot_user.submissions.new())
# Iterate over the bot's past comments update tqdm
if bot_comments:
    for comment in bot_comments:
        # Add the comment ID to the commented_ids set
        commented_ids.add(comment.id)
# Iterate over the bot's past submissions update tqdm
if bot_submissions:
    for submission in bot_submissions:
        # Add the submission ID to the commented_ids set
        commented_ids.add(submission.id)
# log that the bot's past comments and submissions have been added to the commented_ids set
logger.info("Bot's past comments and submissions added to commented_ids set")

# Uses AI to reply to comments and submissions
def prompt(comment, submission, pbar=None):
    # ask user which model to use
    model = Prompt.ask("Which model do you want to use?", choices=[
                       "davinci", "curie", "babbage", "ada"], default="davinci")
    # Ask user for custom prompt
    custom_prompt = Prompt.ask("How would you like the model to reply to this comment/submission?",
                               default="Reply to the following directly and as an expert in under 50 words:")
    # Ask user if they want to reply to the comment/submission
    response = Prompt.ask(
        "Do you want to reply to this comment/submission?", choices=["y", "n"])
    # clear the console
    if response == "y":
        # Get the text of the comment or submission
        try:
            text = comment.body
        except AttributeError:
            text = submission.selftext
        # log that the text is being generated
        logger.info("Generating response to:" + text)
        # Generate a response using OpenAI
        response = openai.Completion.create(
            engine=model,
            prompt=custom_prompt + text + "Reply:",
            max_tokens=50,
            temperature=0.5,
            top_p=1,
            n=1,
            stream=False,
            logprobs=None,
            stop=["\n"],
        )
        # log that the response was generated
        logger.info("Response generated:" + response["choices"][0]["text"])
        # Get the text of the response
        try:
            text = response["choices"][0]["text"]
            # log that the text was retrieved
            logger.info("Response text retrieved")
        except KeyError:
            text = None
            # log that the text was not retrieved
            logger.info("Response text not retrieved")
        # If a response was generated by OpenAI
        if text:
            # log that the response is being replied to
            logger.info("Replying to comment/submission")
            # Reply to the comment or submission
            try:
                comment.reply(text)
            except AttributeError:
                submission.reply(text)
            # Add the comment or submission ID to the commented_ids set
            try:
                data = comment.id
            except AttributeError:
                data = submission.id
            commented_ids.add(data)
            # log that the comment/submission was replied to
            logger.info("Comment/Submission replied to")
            # update tqdm progress bar
            if pbar is not None:
                pbar.set_description(f"Commented_ids set updated with {data}")
                pbar.update(1)
            else:
                print(f"Commented_ids set updated with {data}", end="\r")
            commented_ids.add(data)
            # log that the comment/submission was replied to
            logger.info("Comment/Submission replied to")
            # sleep
            time.sleep(1)
            # end the function
            return

# Stream comments and submissions
def stream_data(subreddit_name, keyword):
    # Get the subreddit object
    subreddit = reddit.subreddit(subreddit_name)
    # Initialize a tqdm object
    pbar = tqdm(total=None, desc=f"\033[34mMonitoring /r/\033[95m{subreddit_name}\033[34m for '\033[95m{keyword}\033[34m'\033[0m", ncols=100,
                bar_format='\033[34m{desc}\033[0m \033[96m|\033[0m \033[34m\033[96m[\033[34mProcessed comments and posts: \033[95m{n_fmt}\033[34m\033[96m]\033[0m \033[96m|\033[0m \033[34m\033[96m[\033[34mElapsed: \033[95m{elapsed}\033[34m\033[96m]\033[0m \033[96m|\033[0m \033[34m\033[96m[\033[34mRate:\033[95m{rate_fmt}\033[34m\033[96m{postfix}\033[96m]\033[0m')
    # Iterate over the stream of submissions in the subreddit
    for submission in subreddit.stream.submissions():
        # Update tqdm to increase the progress bar
        pbar.update()
        # add the submission id to the seen_ids set
        seen_ids.add(submission.id)
        # Check if the keyword is in the submission selftext and if the submission has not been replied to
        if keyword in submission.selftext and submission.id not in commented_ids:
            # Print the submission selftext
            pbar.write(submission.selftext)
            # pause pbar and clear the console
            pbar.clear()
            # Reply to the submission
            prompt(None, submission)
            # Exit the function
            return
        # Iterate over the comments in the submission
        for comment in submission.comments.list():
            # Check if the keyword is in the comment body and if the comment has not been replied to
            if isinstance(comment, Comment):
                if keyword in comment.body and comment.id not in commented_ids:
                    # Print the comment body
                    pbar.write(comment.body)
                    # Reply to the comment
                    prompt(comment, None)
                    # Close the tqdm object
                    pbar.close()
                    # Exit the function
                    return
    # Close the tqdm object
    pbar.close()

# Run the bot on a loop
def main():
    try:
        while True:
            stream_data(subreddit_name, keyword)
    except KeyboardInterrupt:
        # Handle KeyboardInterrupt exception
        logger.info("KeyboardInterrupt exception handled")
        # Ask user if they want to exit
        # clear the console
        os.system("cls" if os.name == "nt" else "clear")
        response = Prompt.ask("Do you want to exit? ", choices=["y", "n"])
        if response == "y":
            # Convert the start and end timestamps to human-readable strings
            start_time_str = datetime.datetime.fromtimestamp(
                start_time).strftime('%Y-%m-%d %H:%M:%S')
            end_time_str = datetime.datetime.fromtimestamp(
                time.time()).strftime('%Y-%m-%d %H:%M:%S')
            # Calculate the elapsed time
            elapsed_time = time.time() - start_time
            # Convert the elapsed time to a timedelta object
            elapsed_time_delta = datetime.timedelta(seconds=elapsed_time)
            # Convert the timedelta object to a number of seconds
            elapsed_time_seconds = elapsed_time_delta.total_seconds()
            # Convert the elapsed time to a datetime object
            elapsed_time_datetime = datetime.datetime.fromtimestamp(
                elapsed_time_seconds)
            # Convert the timedelta object to a human-readable string
            elapsed_time_str = elapsed_time_datetime.strftime('%H:%M:%S')
            # log that the program is exiting
            logger.info("Exiting program")
            #clear the last line
            sys.stdout.write("\033[F")
            # Exit the program
            sys.exit(print(f"Shutting down...\n"
                           f"  Comments and submissions seen: {len(seen_ids):>5}\n"
                           f"  Comments and submissions replied to: {len(commented_ids):>5}\n"
                           f"  Start time: {start_time_str:<25}\n"
                           f"  End time: {end_time_str:<25}\n"
                           f"  Elapsed time: {elapsed_time_str:<25}"))
        else:
            # clear the console
            os.system("cls" if os.name == "nt" else "clear")
            # Run the bot on a loop
            main()


if __name__ == "__main__":
    main()
