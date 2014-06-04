"""
GitHub
"""

from kochira.service import Service
from kochira.service import Config
from kochira import config
import github3

service = Service(__name__, __doc__)

@service.config
class Config(Config):
    access_token = config.Field(doc="GitHub access token")

@service.command(r"!(gh|github) (?P<url>.*)$")
def get_commit_message(ctx, url):
    """
    Get commit message for url given
    """
    line = url.strip().split('/')
    OWNER = line[3]
    REPO = line[4]
    COMMIT = line[6]
    messages = github3.login(token=ctx.config.access_token). \
      repository(OWNER, REPO).commit(COMMIT).commit.message.split('\n')
    for message in messages:
        ctx.message(message)
