import os
import re
from django.core.management.base import BaseCommand
from blog.models import Post
from django.conf import settings

class Command(BaseCommand):
    help = "Clean up orphaned Trix uploads"

    def handle(self, *args, **options):
        # Collect all referenced files in posts
        used_files = set()
        pattern = re.compile(r'src="([^"]+)"')

        for post in Post.objects.all():
            matches = pattern.findall(post.content or "")
            for url in matches:
                if url.startswith(settings.MEDIA_URL):
                    used_files.add(url.replace(settings.MEDIA_URL, "").lstrip("/"))

        # Scan uploads directory
        uploads_directory = os.path.join(settings.MEDIA_ROOT, "uploads")
        for _, _, files in os.walk(uploads_directory):
            for filename in files:
                file_path = os.path.join("uploads", filename)
                if file_path not in used_files:
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    if os.path.isfile(full_path):
                        os.remove(full_path)
                        self.stdout.write(f"Deleted orphan file: {file_path}")
