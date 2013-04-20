#!/usr/bin/python

# Copyright (C) 2013 Gerwin Sturm, FoldedSoft e.U.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""RequestHandlers for Demo services"""

__author__ = 'scarygami@gmail.com (Gerwin Sturm)'

import utils
from auth import get_auth_service
from github import Github

import random
import string
import json

from oauth2client.client import AccessTokenRefreshError

prev = ""

def getGithubNotifications(usr, psw):
    g = Github(usr, psw)
    for note in g.get_user().get_notifications():
        return str(note.repository.name + ": " + note.subject.title)
    return "No Notifications"

class IndexHandler(utils.BaseHandler):
    def get(self):
        template = utils.JINJA.get_template("templates/service.html")
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
        self.session["state"] = state
        self.response.out.write(template.render({"client_id": utils.CLIENT_ID, "state": state}))


class ListHandler(utils.BaseHandler):
    def get(self):
        """Retrieve timeline cards for the current user."""

        self.response.content_type = "application/json"

        gplus_id = self.session.get("gplus_id")
        service = get_auth_service(gplus_id)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return
        try:
            # Retrieve timeline cards and return as reponse
            result = service.timeline().list().execute()
            self.response.status = 200
            self.response.out.write(json.dumps(result))
        except AccessTokenRefreshError:
            self.response.status = 500
            self.response.out.write(utils.createError(500, "Failed to refresh access token."))


class NewCardHandler(utils.BaseHandler):
    def post(self):
        global prev
        self.response.content_type = "application/json"
        gplus_id = self.session.get("gplus_id")
        
        service = get_auth_service(gplus_id)

        if service is None:
            self.response.status = 401
            self.response.out.write(utils.createError(401, "Current user not connected."))
            return

        message = self.request.body

        data = json.loads(message)

        body = {}
        
        current = str(getGithubNotifications("kdietze3", "mcintosh94"))
        if current != prev:
            prev = current
            body["text"] = current
            image = "http://fc08.deviantart.net/fs70/f/2011/180/7/f/guthub_octocat_by_side_7-d3kft7p.png"
            # if "image" in data:
            body["attachments"] = [{"contentType": "image/*", "contentUrl": image}]
            body["menuItems"] = [{"action": "SHARE"}, {"action": "REPLY"}]
            try:
                result = service.timeline().insert(body=body).execute()
                self.response.status = 200
                self.response.out.write(json.dumps(result))
            except AccessTokenRefreshError:
                self.response.status = 500
                self.response.out.write(utils.createError(500, "Failed to refresh access token."))
        else:
            self.response.out.write("Same Notification as Previous")

    


SERVICE_ROUTES = [
    ("/", IndexHandler),
    ("/list", ListHandler),
    ("/new", NewCardHandler)
]
