import requests

from config import cfg


class FacebookAdapter:
    """Custom Adapter for Facebook Social Authentication.

    Attributes:
        access_token_url (str): URL that is used for getting access token from social provider.
        profile_url (str): URL that is used for getting profile info from social provider.
    """
    access_token_url = "https://graph.facebook.com/v14.0/oauth/access_token"
    profile_url = "https://graph.facebook.com/me"

    def get_access_token_data(self, code: str):
        """Method for exchanging authorization code for access token.

        Here we specify all necessary info (i.e. client_id, client_secret) for Facebook provider
        and send request to `access_token_url` to get access token.

        Args:
            code (str): Authorization code.
        """
        facebook_client_id = getattr(cfg, 'facebook_client_id')
        facebook_client_secret = getattr(cfg, 'facebook_client_secret')
        facebook_redirect_uri = getattr(cfg, 'facebook_redirect_uri')
        scope = 'public_profile'

        params = {
            'client_id': facebook_client_id,
            'client_secret': facebook_client_secret,
            'redirect_uri': facebook_redirect_uri,
            'code': code,
            'scope': scope
        }
        resp = requests.get(self.access_token_url, params=params)
        if resp.status_code != 200:
            raise ValueError(
                'Unable to obtain Access Token. Please double-check the info you are sending to `access_token_url`'
            )
        access_token = resp.json().get('access_token', None)
        return access_token

    def get_profile_data(self, access_token: str):
        """Method for exchanging access token for profile info.

        Here we use `access_token` to get Facebook account's profile info.

        Args:
            access_token (str): Access token.

        """
        params = {
            'fields': 'email',
            'access_token': access_token
        }
        resp = requests.get(self.profile_url, params=params)
        profile_info = resp.json()
        return profile_info
