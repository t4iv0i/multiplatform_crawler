NUM_OF_WORKERS = 1
MAX_RETRY_LOADING = 3
CONVERT_COLLECTION_NAME = {
    "user": "User", "page": "Page", "group": "Group", "event": "Event", "post": "Post", "pagepost": "PagePost",
    "album": "Album", "video": "Video"
}

REQUIRED_FOLLOWER = 2000
BATCH_LIMIT = 1000
delay = 15
FACEBOOK_GRAPH_API_URL = "https://graph.facebook.com"
DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"

teen_code = dict(K=1000, M=1000000)
url_patterns = dict(facebook=[r'([^/]*facebook\.com/profile.php\?id=[^/\?#]+)',
                              r'([^/]*facebook\.com/groups/[^/\?#]+)',
                              r'([^/]*facebook\.com/[^/\?#]+)'],
                    instagram=[r'([^/]*instagram\.com/[^/\?#]+)'],
                    tiktok=[r'([^/]*tiktok\.com/[^/\?#]+)'],
                    youtube=[r'([^/]*youtube\.com/[channel/]*[^/\?#]+)',
                             r'([^/]*youtu\.be/[^/\?#]+)'])

check_ipv4_address = "https://api.ipify.org"
check_ipv6_address = "https://ipv6-test.com/"
type_of_proxy = ["available", "active", "dead"]

type_of_credential = ["account", "token", "cookie"]
facebook_get_access_token_url = "https://www.facebook.com/dialog/oauth?client_id=124024574287414&redirect_uri=https://www.instagram.com/accounts/signup/&scope=email&response_type=token"

mbasic_facebook_email_xpath = "//*[@id='m_login_email']"
mbasic_facebook_password_xpath = "//*[@id='password_input_with_placeholder']/input"
mbasic_facebook_login_button_xpath = "//*[@id='login_form']/ul/li[3]/input"
mbasic_facebook_2fa_input_xpath = "//*[@id='approvals_code']"
mbasic_facebook_2fa_dont_save_xpath = "//section/section/div//label/input[@type='radio' and @value='dont_save']"
mbasic_facebook_2fa_submit_button_xpath = "//*[@id='checkpointSubmitButton-actual-button']"
mbasic_facebook_next_button_xpath = "//*[@id='checkpointSubmitButton-actual-button']"
mbasic_facebook_about_selector = "#root > div.bi.bj > div.bk > div.bv.bw.bx > div.co.cp.cq.cr"
mbasic_facebook_id_patterns = [r'[\_\;]id=(\d+)',
                               r'thread\/(\d+)',
                               r'groups\/(\d+)']

instagram_facebook_login_button_xpath = "//*[@id='loginForm']/div/div[5]/button/span[2]"
instagram_facebook_confirm_button_xpath = "//*[@id='u_0_x_Oa']/div[1]/div/div/div[3]/button[1]"



