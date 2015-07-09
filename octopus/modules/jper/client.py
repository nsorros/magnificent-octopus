from octopus.core import app
from octopus.modules.jper import models
from octopus.lib import http
import json

class JPERException(Exception):
    pass

class ValidationException(Exception):
    pass

class JPER(object):

    FilesAndJATS = "http://router.jisc.ac.uk/packages/FilesAndJATS"

    def __init__(self, api_key=None, base_url=None):
        self.api_key = api_key if api_key is not None else app.config.get("JPER_API_KEY")
        self.base_url = base_url if base_url is not None else app.config.get("JPER_BASE_URL")

    def _url(self, endpoint=None, id=None, auth=True):
        url = self.base_url
        if not url.endswith("/"):
            url += "/"

        if endpoint is not None:
            url += endpoint

        if id is not None:
            url += "/" + http.quote(id)

        if auth:
            url += "?api_key=" + http.quote(self.api_key)

        return url

    def validate(self, notification, file_handle=None):
        # turn the notification into a json string
        data = None
        if isinstance(notification, models.IncomingNotification):
            data = notification.json()
        else:
            data = json.dumps(notification)

        # get the url that we are going to send to
        url = self._url("validate")

        resp = None
        if file_handle is None:
            # if there is no file handle supplied, send the metadata-only notification
            resp = http.post(url, data=data, headers={"Content-Type" : "application/json"})
        else:
            # otherwise send both parts as a multipart message
            files = [
                ("metadata", ("metadata.json", data, "application/json")),
                ("content", ("content.zip", file_handle, "application/zip"))
            ]
            resp = http.post(url, files=files)

        if resp is None:
            raise JPERException("Unable to communicate with the JPER API")

        if resp.status_code == 401:
            raise JPERException("Could not authenticate with JPER with your API key")

        if resp.status_code == 400:
            raise ValidationException(resp.json().get("error"))

        return True

    def create_notification(self, notification, file_handle=None):
        # turn the notification into a json string
        data = None
        if isinstance(notification, models.IncomingNotification):
            data = notification.json()
        else:
            data = json.dumps(notification)

        # get the url that we are going to send to
        url = self._url("notification")

        resp = None
        if file_handle is None:
            # if there is no file handle supplied, send the metadata-only notification
            resp = http.post(url, data=data, headers={"Content-Type" : "application/json"})
        else:
            # otherwise send both parts as a multipart message
            files = [
                ("metadata", ("metadata.json", data, "application/json")),
                ("content", ("content.zip", file_handle, "application/zip"))
            ]
            resp = http.post(url, files=files)

        if resp is None:
            raise JPERException("Unable to communicate with the JPER API")

        if resp.status_code == 401:
            raise JPERException("Could not authenticate with JPER with your API key")

        if resp.status_code == 400:
            raise ValidationException(resp.json().get("error"))

        # extract the useful information from the acceptance response
        acc = resp.json()
        id = acc.get("id")
        loc = acc.get("location")

        return id, loc

    def get_notification(self, notification_id=None, location=None):
        # get the url that we are going to send to
        if notification_id is not None:
            url = self._url("notification", id=notification_id)
        elif location is not None:
            url = location
        else:
            raise JPERException("You must supply either the notification_id or the location")

        # get the response object
        resp = http.get(url)

        if resp.status_code != 200:
            raise JPERException("Received unexpected status code: {x}".format(x=resp.status_code))

        j = resp.json()
        if "provider" in j:
            return models.ProviderOutgoingNotification(j)
        else:
            return models.OutgoingNotification(j)

    def get_content(self, notification_id):
        pass

    def list_notifications(self, since, page=None, page_size=None, repository_id=None):
        return None

    def record_retrieval(self, notification_id, content_id=None):
        pass