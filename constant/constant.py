NUM_OF_API_CRAWLERS = 30
NUM_OF_FACEBOOK_CRAWLERS = 4
NUM_OF_INSTAGRAM_CRAWLERS = 5
NUM_OF_TIKTOK_CRAWLERS = 5
NUM_OF_YOUTUBE_CRAWLERS = 1
NUM_OF_DAEMONS_CRAWLERS = 4
NUM_OF_WORKERS = 1
NUM_OF_DB_SESSION = 3
MAX_RETRY_LOADING = 3
MAX_RETRY_WORKER = 2
CONVERT_COLLECTION_NAME = {
    "user": "User", "page": "Page", "group": "Group", "event": "Event", "post": "Post", "pagepost": "PagePost",
    "album": "Album", "video": "Video"
}

REQUIRED_FOLLOWER = 2000
BATCH_LIMIT = 1000
delay = 15
FACEBOOK_GRAPH_API_URL = "https://graph.facebook.com"
# FACEBOOK_DEFAULT_PARAMS = {
#     "connection": [
#         {
#             "collection": "Post",
#             "connection_name": "posts",
#             "condition": {"duration": "30 days"}
#         },
#     ]
# }
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

check_ipv4_address = "https://api.ipify.org"
check_ipv6_address = "https://ipv6-test.com/"
teen_code = dict(K=1000, M=1000000)
url_patterns = dict(facebook=[r'([^/]*facebook\.com/profile.php\?id=[^/\?#]+)',
                              r'([^/]*facebook\.com/groups/[^/\?#]+)',
                              r'([^/]*facebook\.com/[^/\?#]+)'],
                    instagram=[r'([^/]*instagram\.com/[^/\?#]+)'],
                    tiktok=[r'([^/]*tiktok\.com/[^/\?#]+)'],
                    youtube=[r'([^/]*youtube\.com/[channel/]*[^/\?#]+)',
                             r'([^/]*youtu\.be/[^/\?#]+)'])

facebook_get_access_token_url = "https://www.facebook.com/dialog/oauth?client_id=124024574287414&redirect_uri=https://www.instagram.com/accounts/signup/&scope=email&response_type=token"
facebook_about_selector = "#root > div.bi.bj > div.bk > div.bv.bw.bx > div.co.cp.cq.cr"
facebook_id_patterns = [r'[\_\;]id=(\d+)',
                        r'thread\/(\d+)',
                        r'groups\/(\d+)']

instagram_indicators = dict(name=["full_name"],
                            username=["graphql", "user", "username"],
                            id=["id"],
                            post=["edge_owner_to_timeline_media", "count"],
                            follower=["edge_followed_by", "count"],
                            following=["edge_follow", "count"],
                            description=["biography"])

tiktok_info_xpath = {
    "username": "/html/body//h2[contains(@data-e2e, 'user-title') or contains(@class, 'share-title')]",
    "name": "/html/body//h1[contains(@data-e2e, 'user-subtitle') or contains(@class, 'share-sub-title')]",
    "follower": "/html/body//strong[contains(@title, 'Follower') or contains(@data-e2e, 'followers-count')]",
    "following": "/html/body//div/strong[contains(@title, 'Following') or contains(@title, 'Đang Follow') or contains(@data-e2e, 'following-count')]",
    "like": "/html/body//strong[contains(@title, 'Likes') or contains(@title, 'Thích') or contains(@data-e2e, 'likes-count')]",
    "description": "/html/body//h2[contains(@class, 'share-desc') or contains(@data-e2e, 'user-bio')]",
    "share_link": "/html/body//div[contains(@class, 'share-links')]/a"
}

youtube_info_xpath = {
    "name": "//*[@id='text-container']",
    "follower": "//*[@id='subscriber-count']",
    "view": "//*[@id='right-column']/yt-formatted-string[3]",
    "description": "//*[@id='description-container']/yt-formatted-string[2]",
    "detail": "//*[@id='details-container']/table",
    "date_joined": "//*[@id='right-column']/yt-formatted-string[2]"
}
