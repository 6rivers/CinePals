from flask import url_for
from application import app
from application import social_oauth


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):
    def __init__(self):
        super(GoogleSignIn, self).__init__('google')
        CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
        social_oauth.register(
            name='google',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            server_metadata_url=CONF_URL,
            client_kwargs={
                'scope': 'openid email profile'
            }
        )

    def authorize(self):
        redirect_uri = self.get_callback_url()
        # print(f"printing redirect_uri {redirect_uri}")
        return social_oauth.google.authorize_redirect(redirect_uri)

    def callback(self):
        token = social_oauth.google.authorize_access_token()
        # print(f'printing Google token {token}')
        userinfo = token['userinfo']
        name = userinfo['given_name']
        email = userinfo['email']
        social_id = userinfo['sub']
        picture = userinfo['picture']
        # print(" Google userinfo ", userinfo)
        # print(f"Name of the user is {name} and email is {email}, social_id is {social_id}")
        return (name, email, social_id, picture)
