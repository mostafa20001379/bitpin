from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.auth.models import User
from ratings.models import Content, Rating
import random
from tqdm.auto import tqdm

class Command(BaseCommand):
    help = 'Seeds the database with sample content, users, and ratings'

    def handle(self, *args, **kwargs):
        try:
            # Clear existing data
            self.stdout.write("Deleting old data...")
            Rating.objects.all().delete()
            Content.objects.all().delete()
            User.objects.filter(username__startswith='user_').delete()

            # Reset the auto-incrementing ID for Content table
            with connection.cursor() as cursor:
                # For PostgreSQL
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        TRUNCATE TABLE ratings_content RESTART IDENTITY CASCADE;
                    """)
                
                # For SQLite
                elif connection.vendor == 'sqlite':
                    cursor.execute("""
                        DELETE FROM sqlite_sequence WHERE name='ratings_content';
                    """)
                
                # For MySQL
                elif connection.vendor == 'mysql':
                    cursor.execute("""
                        ALTER TABLE ratings_content AUTO_INCREMENT = 1;
                    """)

            self.stdout.write(self.style.SUCCESS("Successfully reset content table and its ID sequence"))

            # Continue with your seeding logic here
            # ...

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))

        # Create a superuser
        self.stdout.write("Creating superuser...")
        if not User.objects.filter(username='bitpin').exists():
            User.objects.create_superuser(
                username='bitpin',
                email='bitpin@example.com',
                password='1234'
            )

        # Seed users
        self.stdout.write("Creating users...")
        users = []
        for i in tqdm(range(200)):
            user = User.objects.create_user(
                username=f"user_{i}",
                password="1234"
            )
            users.append(user)

        # Seed content
        self.stdout.write("Creating content...")
        contents = []
        for i in tqdm(range(50)):
            content = Content.objects.create(
                title=f"Content Title {i}",
                text=f"This is the text of content item {i}."
            )
            contents.append(content)

        # Seed ratings
        self.stdout.write("Creating ratings...")
        for content in contents:
            for user in random.sample(users, 100):  # Assign ratings from a random subset of users
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
