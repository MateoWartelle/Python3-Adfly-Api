# -*- coding: utf-8 -*-

import json
import hashlib
import hmac
import time
import urllib

from restful_lib import Connection


class AdflyApiExample():
    #FROM EXAMPLE
##    BASE_HOST = 'https://api.adf.ly'
##    # TODO: Replace this with your secret key.
##    SECRET_KEY = '4c8fa05a-d826-4c06-86e4-59b86bf4868c'
##    # TODO: Replace this with your public key.
##    PUBLIC_KEY = '2ba3f6ce601d043c177eb2a83eb34f5f'
##    # TODO: Replace this with your user id.
##    USER_ID = 2
##    AUTH_TYPE = dict(basic=1, hmac=2)
    
    BASE_HOST = 'https://api.adf.ly'
    SECRET_KEY = 'YOUR SECRET KEY'
    PUBLIC_KEY = 'YOUR PUBLIC KEY'
    USER_ID = 'YOUR USER ID'
    AUTH_TYPE = dict(basic=1, hmac=2)
    
    def __init__(self):
        # In this example we use rest client provided by
        # http://code.google.com/p/python-rest-client/
        # Of course you are free to use any other client.
        self._connection = Connection(self.BASE_HOST)
    
    def get_groups(self, page=1):
        response = self._connection.request_get(
            '/v1/urlGroups',
            args=self._get_params(dict(_page=page), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def expand(self, urls, hashes=[]):
        params = dict()
        
        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls
        
        if type(hashes) == list:
            for i, hashval in enumerate(hashes):
                params['hash[%d]' % i] = hashval
        elif type(hashes) == str:
            params['hash'] = hashes
        
        response = self._connection.request_get(
            '/v1/expand',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])
    
    def shorten(self, urls, domain=None, advert_type=None, group_id=None):
        params = dict()
        if domain:
            params['domain'] = domain
        if advert_type:
            params['advert_type'] = advert_type
        if group_id:
            params['group_id'] = group_id
        
        if type(urls) == list:
            for i, url in enumerate(urls):
                params['url[%d]' % i] = url
        elif type(urls) == str:
            params['url'] = urls
        
        response = self._connection.request_post(
            '/v1/shorten',
            args=self._get_params(params, self.AUTH_TYPE['basic']))
        return json.loads(response['body'])
    
    def get_urls(self, page=1, search_str=None):
        response = self._connection.request_get(
            '/v1/urls',
            args=self._get_params(dict(_page=page, q=search_str), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def update_url(self, url_id, **kwargs):
        params = dict()
        
        allowed_kwargs = ['url', 'advert_type', 'title',
                          'group_id', 'fb_description', 'fb_image']
        for k, v in kwargs.items():
            if k in allowed_kwargs:
                params[k] = v
        
        response = self._connection.request_put(
            '/v1/urls/%d' % url_id,
            args=self._get_params(params, self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def delete_url(self, url_id):
        response = self._connection.request_delete(
            '/v1/urls/%d' % url_id,
            args=self._get_params(dict(), self.AUTH_TYPE['hmac']))
        return json.loads(response['body'])
    
    def _get_params(self, params={}, auth_type=None):
        """Populates request parameters with required parameters,
        such as _user_id, _api_key, etc.
        """
        auth_type = auth_type or self.AUTH_TYPE['basic']
        
        params['_user_id'] = self.USER_ID
        params['_api_key'] = self.PUBLIC_KEY
        
        if self.AUTH_TYPE['basic'] == auth_type:
            pass
        elif self.AUTH_TYPE['hmac'] == auth_type:
            # Get current unix timestamp (UTC time).
            params['_timestamp'] = int(time.time())
            params['_hash'] = self._do_hmac(params)
        else:
            raise RuntimeError
        
        return params

    def _do_hmac(self, params):
        if type(params) != dict:
            raise RuntimeError
        
        # Get parameter names.
        keys = params.keys()
        # Sort them using byte ordering.
        # So 'param[10]' comes before 'param[2]'.
        keys.sort()
        queryParts = []
        
        # Url encode query string. The encoding should be performed
        # per RFC 1738 (http://www.faqs.org/rfcs/rfc1738)
        # which implies that spaces are encoded as plus (+) signs.
        for key in keys:
            quoted_key = urllib.quote_plus(str(key))
            if params[key] is None:
                params[key] = ''
            
            quoted_value = urllib.quote_plus(str(params[key]))
            queryParts.append('%s=%s' % (quoted_key, quoted_value))
        
        return hmac.new(
            self.SECRET_KEY,
            '&'.join(queryParts),
            hashlib.sha256).hexdigest()

def convert_to_adfly(URL):
    api = AdflyApiExample()
    Temp = json.dumps(api.shorten(URL))
    resp_dict = json.loads(Temp) #Load JSON into dictionary
    return (resp_dict["data"][0]["short_url"]) #Prints dictionary value of short_url

def main():
    print (convert_to_adfly("www.google.com"))
    
    # Url Groups examples.
    #print json.dumps(api.get_groups(), indent=4)
    
    # Expand examples.
    #print json.dumps(api.expand(
    #    ['http://adf.ly/D', 'http://adf.ly/E', 'http://q.gs/4'],
    #    [3, '1A', '1C']), indent=4)
    #print json.dumps(api.expand(None, '1F'), indent=4)
    
    # Shorten examples.
    #print json.dumps(api.shorten(
    #    ['http://docs.python.org/library/json.html',
    #     'http://www.doughellmann.com/PyMOTW/hmac/'],
    #    'q.gs', 'banner', None), indent=4)
    #print json.dumps(
    #    api.shorten('http://docs.python.org/library/json.html'), 
    #    indent=4)
    
    # Urls examples.
    #print json.dumps(api.get_urls(), indent=4)
    #print json.dumps(api.get_urls(search_str='htmlbook'), indent=4)
    #print json.dumps(api.update_url(136, advert_type='int', group_id=None), indent=4)
    #print json.dumps(api.update_url(136, title='一些中国', fb_description='fb о+писан  и+е', fb_image='123'), indent=4)
    #print json.dumps(api.delete_url(136), indent=4)

if __name__ == '__main__':
    main()
