import requests

from config import cfg


class GoogleAdapter:
    """Custom Adapter for Google Social Authentication.

    Attributes:
        access_token_url (str): URL that is used for getting access token from social provider.
        profile_url (str): URL that is used for getting profile info from social provider.
    """
    access_token_url = "https://accounts.google.com/o/oauth2/token"
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    def get_access_token_data(self, code: str):
        """Method for exchanging authorization code for access token.

        Here we specify all necessary info (i.e. client_id, client_secret) for Google provider
        and send request to `access_token_url` to get access token.

        Args:
            code (str): Authorization code.
        """
        google_client_id = getattr(cfg, 'google_client_id')
        google_client_secret = getattr(cfg, 'google_client_secret')
        google_redirect_uri = getattr(cfg, 'google_redirect_uri')
        scope = 'https://www.googleapis.com/auth/userinfo.profile'
        grant_type = 'authorization_code'

        data = {
            'client_id': google_client_id,
            'client_secret': google_client_secret,
            'redirect_uri': google_redirect_uri,
            'code': code,
            'scope': scope,
            'grant_type': grant_type
        }
        resp = requests.post(self.access_token_url, data=data)
        if resp.status_code != 200:
            raise ValueError(
                'Unable to obtain Access Token. Please double-check the info you are sending to `access_token_url`'
            )
        access_token = resp.json().get('access_token', None)
        return access_token

    def get_profile_data(self, access_token: str):
        """Method for exchanging access token for profile info.

        Here we use `access_token` to get Google account's profile info.

        Args:
            access_token (str): Access token.

        """
        resp = requests.get(
            self.profile_url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_info = resp.json()
        return profile_info
