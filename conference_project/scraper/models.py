from django.db import models

class ConferenceItem(models.Model):

    SESSION_TYPES = [
        ('Session', 'Session'),
        ('Poster', 'Poster')
    ]

    session_title = models.CharField(max_length=500, default="N/A")
    session_type = models.CharField(max_length=50, choices=SESSION_TYPES)

    poster_title = models.TextField(blank=True, null=True)

    authors = models.TextField(blank=True, null=True)
    affiliations = models.TextField(blank=True, null=True)

    date = models.CharField(max_length=50, blank=True, null=True)
    time = models.CharField(max_length=50, blank=True, null=True)

    location = models.CharField(max_length=255, blank=True, null=True)

    session_category = models.CharField(max_length=255, blank=True, null=True)

    presentation_type = models.CharField(max_length=255, blank=True, null=True)

    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.session_type == "Poster":
            return f"Poster: {self.poster_title or self.session_title}"
        return f"Session: {self.session_title}"