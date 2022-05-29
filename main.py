from datetime import datetime, timedelta
from instaloader import Instaloader, Profile
from credentials import USERNAME, PASSWORD

from sql_functions import *
from rich.console import Console

# week_ago = datetime.now() - timedelta(days=15)

all_data = query_all(["owner","post_date"])
all_data['post_date'] = all_data['post_date'].apply(lambda date: datetime.strptime(date, "%H:%M:%S %d %b %Y"))
latest_post = all_data.groupby("owner").max()
latest_post = latest_post.T.to_dict()

L = Instaloader()
L.login(USERNAME,PASSWORD)

barkas_account = [
    "barkas.jogjakarta",
    "infobarkas_jogja"
]

current = datetime.now()

console = Console()
with console.status("[green]program starting[/]") as status:
    for username in barkas_account:
        profile = Profile.from_username(L.context,username)
        i = 0
        for post in profile.get_posts():
            status.update(f"[green]Collecting post from {username} ({i})[/]")
            timestamp = int(post.date_local.timestamp())
            date = datetime.fromtimestamp(timestamp)
            if date > latest_post[username]['post_date'] and post.caption != None:
            # if date > week_ago:
                entry = {
                    "shortcode": post.shortcode,
                    "timestamp": timestamp,
                    "latest_update": current.strftime("%H:%M:%S %d %b %Y"),
                    "post_date": date.strftime("%H:%M:%S %d %b %Y"),
                    "post_url": "https://www.instagram.com/p/"+post.shortcode+"/",
                    "thumbnail": post.url,
                    "owner": post.owner_username,
                    "caption": post.caption,
                    "label": "ADS" if len(post.tagged_users) > 0 else None,
                    "likes": post.likes,
                    "comments": post.comments,
                    "mentioned": ";;".join(post.caption_mentions),
                    "tagged": ";;".join(post.tagged_users),
                    "hashtags": ";;".join(post.caption_hashtags),
                    "is_video": post.is_video,
                    "type": post.typename
                }
                insert(entry)
                i += 1
            else:
                break