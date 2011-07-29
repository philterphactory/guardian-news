# Copyright (C) 2011 Philter Phactory Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of Philter Phactory Ltd. shall
# not be used in advertising or otherwise to promote the sale, use or other
# dealings in this Software without prior written authorization from Philter
# Phactory Ltd.

import logging
import random

from base_prosthetic import Prosthetic, persist_state

import guardianapi

import models

NUM_SEARCH_TERMS = 1
MAX_MAIN_LENGTH = 1024

class GuardianNews(Prosthetic):
    """A prosthetic that finds news items based on the Weavr's state."""

    # run throttle
    @classmethod
    def time_between_runs(cls):
        # seconds
        return 7200

    def api_client(self):
        config = models.guardian_news_config()
        return guardianapi.Client(config.api_key)

    def get_news(self, keywords):
        """Get a news item for the keywords, or raise an exception"""
        client = self.api_client()
        results = client.search(q=keywords, order_by='newest')
        #logging.info(str(results))
        item = random.choice(results.results())
        item_details = client.item(item['id'], show_fields='all',
                                   order_by='newest')
        #logging.info(str(item_details))
        return item_details

    def search_terms(self, run):
        """Create a list of search terms from the run"""
        all_terms = run['combined_keywords'].split()
        subset = random.sample(all_terms, NUM_SEARCH_TERMS)
        return " ".join(subset)

    def format_news(self, item):
        fields = item['fields']
        main = fields['body']
        if len(main) > MAX_MAIN_LENGTH:
            #FIXME: Smarter turncate...
            main = main[:MAX_MAIN_LENGTH] + '...'
        if main.startswith('<!--'):
            main = fields['trailText'] + '...'
        news = '<p><a href="%s">%s</a></b></p>' % \
            (item['webUrl'], fields['headline'])
        byline = fields.get('byline')
        if byline:
            news += '<p>by <i>%s</i></p>' % byline
        thumbnail = fields.get('thumbnail')
        if thumbnail:
            news += '<img src="%s" />' % thumbnail
        news += '<p>%s</p> <img src="http://image.guardian.co.uk/sys-images/Guardian/Pix/pictures/2010/03/01/poweredbyguardianBLACK.png" />' % main
        return news

    def post_news(self, run, state):
        result = "Posted news item"
        terms = self.search_terms(run)
        item = self.get_news(terms)
        if item and not models.already_posted_news(self.token, item['id']):
            self.post("/1/weavr/post/", {
                    "category":"article",
                    "title":"News about " + terms,
                    "body":self.format_news(item),
                    "keywords":state["emotion"],
                    })
            models.record_posted_news(self.token, item['id'])
            result = "Posted %s" % item['id']
        else:
            result = "Already posted %s" % item['id']
        return result


    # called from the task queue, once an hour (or whatever)
    @persist_state
    def act(self, force=False):
        weavr_state = self.get("/1/weavr/state/")
        if not weavr_state['active'] :
            logging.info("I am not active, leave me alone")
            return None
        if not weavr_state['awake'] :
            logging.info("I am asleep and I dont want to whistle")
            return None
        runs = self.get("/1/weavr/run/")
        if runs:
            run = runs['runs'][0]
            result = self.post_news(run, weavr_state)
        else:
            result = "No runs yet"
        return result
