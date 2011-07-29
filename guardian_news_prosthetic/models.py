from django.db import models

class GuardianNewsConfig(models.Model):
    api_key = models.CharField(max_length=255, blank=False, help_text="your Guardian API key.")

def guardian_news_config():
    try:
        configs = GuardianNewsConfig.objects.order_by('-id')
        return configs[0]
    except IndexError:
        raise Exception("No GuardianNewsConfig object defined")

class GuardianNewsAlreadyPosted(models.Model):
    item_id = models.CharField(max_length=255, blank=False)
    weavr_token = models.ForeignKey('webapp.AccessToken',
                                    related_name='guardian_news_already_posted')

def already_posted_news(token, item_id):
    """Check whether the weavr has already posted the News"""
    try:
        already = GuardianNewsAlreadyPosted.objects.get(weavr_token=token,
                                                        item_id=item_id)
        return True
    except GuardianNewsAlreadyPosted.DoesNotExist:
        return False

def record_posted_news(token, item_id):
    """Record that the weavr has posted the News"""
    posted = GuardianNewsAlreadyPosted(weavr_token=token, item_id=item_id)
    posted.save()
