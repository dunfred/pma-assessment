import uuid
from django.db import models
from apps.user.models import User

def comment_document_upload_location(instance, filename):
    file_extension = filename.split('.')[-1]
    return f"comments/{instance.user.username}/{uuid.uuid4()}.{file_extension}"

# Create your models here.
class Project(models.Model):
    title       = models.CharField(max_length=200)
    description = models.TextField()
    users       = models.ManyToManyField(User, through='ProjectRole', related_name='projects')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ProjectRole(models.Model):
    ROLE_CHOICES = [
        ('OWNER', 'Owner'),
        ('EDITOR', 'Editor'),
        ('READER', 'Reader'),
    ]

    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projectrole')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='projectrole')
    role    = models.CharField(max_length=10, choices=ROLE_CHOICES)
    
    class Meta:
        unique_together = ['user', 'project']
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title} - {self.role}"

class Comment(models.Model):
    project    = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content    = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.title}"

class Document(models.Model):
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_documents')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='documents')
    file    = models.FileField(upload_to=comment_document_upload_location)

    def __str__(self):
        return f"{self.comment} Document"

