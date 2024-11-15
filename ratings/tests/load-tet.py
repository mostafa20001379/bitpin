import asyncio
import aiohttp
import random
import time
from tqdm.asyncio import tqdm
from datetime import datetime
from statistics import mean

# API Endpoints
LOGIN_URL = "http://localhost:8000/api/login/"
CONTENT_URL = "http://localhost:8000/api/contents"

# Mock Data (Users and Content IDs)
USERS = [{"username": f"user_{i}", "password": "1234"} for i in range(1, 201)]
CONTENTS = [i for i in range(1, 51)]
TOKENS = []

class TestStats:
    def __init__(self):
        self.successful = 0
        self.failed = 0
        self.response_times = []

    def add_result(self, status, response_time):
        if status == 201:
            self.successful += 1
        else:
            self.failed += 1
        self.response_times.append(response_time)

    def get_p95_response_time(self):
        if not self.response_times:
            return 0
        sorted_times = sorted(self.response_times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[idx]

async def authenticate_user(session, user):
    """Authenticate a user and return the auth token."""
    payload = {"username": user["username"], "password": user["password"]}
    try:
        async with session.post(LOGIN_URL, json=payload) as response:
            data = await response.json()
            return user["username"], data.get("token")
    except Exception as e:
        print(f"Authentication failed for {user['username']}: {str(e)}")
        return user["username"], None

async def authenticate_all_users(session):
    """Authenticate all users in parallel with progress bar."""
    auth_tasks = [authenticate_user(session, user) for user in USERS]
    auth_results = await tqdm.gather(*auth_tasks, desc="Authenticating users")
    return {username: token for username, token in auth_results if token is not None}

async def send_request(session, username, auth_token, content_id, score, stats):
    """Send a POST request to rate content with the provided auth token."""
    start_time = time.time()
    try:
        payload = {"score": score}
        rate_url = f"{CONTENT_URL}/{content_id}/ratings/"
        headers = {"Authorization": f"Token {auth_token}"}
        async with session.post(rate_url, json=payload, headers=headers) as response:
            response_time = time.time() - start_time
            stats.add_result(response.status, response_time)
            return response.status, await response.text()
    except Exception as e:
        response_time = time.time() - start_time
        stats.add_result(0, response_time)
        return 0, str(e)

async def perform_test(request_rate, duration_seconds):
    """Perform a load test with the specified request rate."""
    stats = TestStats()
    total_requests = request_rate * duration_seconds
    
    async with aiohttp.ClientSession() as session:
        # Authenticate all users first
        print("\nAuthenticating users...")
        auth_tokens = await authenticate_all_users(session)
        
        if not auth_tokens:
            print("No users could be authenticated. Aborting test.")
            return None

        print(f"\nStarting requests at {request_rate} requests/second")
        auth_items = list(auth_tokens.items())  # Convert to list for random selection

        # Create progress bar for all requests
        with tqdm(total=total_requests, desc="Sending requests", unit="req") as pbar:
            tasks = []
            
            # Create all tasks upfront
            for _ in range(total_requests):
                # Randomly select a user for each request
                username, token = random.choice(auth_items)
                content_id = random.choice(CONTENTS)
                score = random.randint(0, 5)
                
                task = send_request(session, username, token, content_id, score, stats)
                tasks.append(task)
                pbar.update(1)
            
            # Execute all tasks with rate limiting
            chunk_size = request_rate
            for i in range(0, len(tasks), chunk_size):
                chunk = tasks[i:i + chunk_size]
                await asyncio.gather(*chunk)
                if i + chunk_size < len(tasks):  # Don't wait after the last chunk
                    await asyncio.sleep(1)  # Wait 1 second before next batch
    
    return stats

async def main():
    """Main function to run the tests."""
    request_rates = [10, 100, 1000]  # Requests per second
    duration_seconds = 10  # Duration for each test
    
    print(f"\nLoad Test Started at {datetime.now()}")
    print(f"Configuration:")
    print(f"- Available Users: {len(USERS)}")
    print(f"- Content Items: {len(CONTENTS)}")
    print(f"- Duration: {duration_seconds} seconds")
    
    for rate in request_rates:
        print(f"\nTest Rate: {rate} requests/sec")
        
        start_time = time.time()
        stats = await perform_test(rate, duration_seconds)
        total_time = time.time() - start_time
        
        if stats:
            total_requests = stats.successful + stats.failed
            actual_rps = total_requests / total_time
            avg_response_time = mean(stats.response_times) if stats.response_times else 0
            p95_response_time = stats.get_p95_response_time()
            
            print("\nTest Results:")
            print(f"Total Requests: {total_requests}")
            print(f"Successful Requests: {stats.successful}")
            print(f"Failed Requests: {stats.failed}")
            print(f"Success Rate: {(stats.successful/total_requests)*100:.2f}%")
            print(f"Actual Requests/Second: {actual_rps:.2f}")
            print(f"Average Response Time: {avg_response_time*1000:.2f}ms")
            print(f"95th Percentile Response Time: {p95_response_time*1000:.2f}ms")
            print(f"Total Test Duration: {total_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())