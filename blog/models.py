from django.db import models
from django.shortcuts import reverse


class Post(models.Model):
    class Meta:
        ordering = ['-id']
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.pk])

    def __str__(self):
        return self.title


class Comment(models.Model):
    class Meta:
        ordering = ['-id']

    post = models.ForeignKey(Post)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)