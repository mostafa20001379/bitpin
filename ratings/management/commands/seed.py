from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ratings.models import Content, Rating
import random


class Command(BaseCommand):
    help = 'Seeds the database with sample content, users, and ratings'

    def handle(self, *args, **kwargs):
        # Clear existing data if necessary
        self.stdout.write("Deleting old data...")
        Rating.objects.all().delete()
        Content.objects.all().delete()
        User.objects.filter(username__startswith='user_').delete()

        # Seed users
        self.stdout.write("Creating users...")
        users = []
        for i in range(10):
            user, created = User.objects.get_or_create(username=f"user_{i}")
            users.append(user)

        # Seed content
        self.stdout.write("Creating content...")
        contents = []
        for i in range(5):
            content = Content.objects.create(
                title=f"Content Title {i}",
                text=f"This is the text of content item {i}."
            )
            contents.append(content)

        # Seed ratings
        self.stdout.write("Creating ratings...")
        for content in contents:
            for user in users:
                score = random.randint(0, 5)
                Rating.objects.create(
                    user=user,
                    content=content,
                    score=score,
                    is_verified=True  # Assume all initial ratings are verified
                )

        # Update cache for each content
        self.stdout.write("Updating cache...")
        for content in contents:
            content.update_cache()

        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
