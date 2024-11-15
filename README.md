# BitPin Rating System

## Project Overview
A high-performance Django REST Framework application for managing content ratings with spam protection mechanisms. The application includes a robust system for detecting and mitigating spam-like behavior, such as rating manipulation through sudden spikes or biased patterns of extremely high or low scores.


## Features
- Content rating system with spam protection
- High-performance caching mechanism
- Rate limiting and verification system
- RESTful API endpoints

## High Load Handling Strategies

To ensure system stability and performance under heavy traffic, the following mechanisms are currently implemented:

1. **Caching**:
   - Redis is used to cache frequently accessed data, such as content ratings and recent rating activity.
   - This reduces the load on the database and improves API response times.

2. **Database Optimization**:
   - Key fields like `content_id`, `user_id`, and `created_at` are properly indexed for faster lookups and queries.
   - Database connection pooling is configured to handle simultaneous connections efficiently.

### Future Optimizations

While the current setup ensures basic stability, the following enhancements are planned to further optimize the system for high load scenarios:

1. **Rate Limiting**:
   - Enforcing request throttling to prevent abuse and protect the system during peak traffic.

2. **Load Balancing**:
   - Deploying the application behind a load balancer (e.g., Nginx, HAProxy) to distribute traffic evenly across multiple instances.

## Spam Detection Mechanism

The application includes a robust spam detection system to prevent manipulation of content ratings. The spam detection logic works as follows:

1. **Rating Spike Detection**:
   - Monitors the number of ratings submitted for a specific content within a short period (e.g., 5 minutes).
   - Flags ratings as unverified if the total exceeds a predefined threshold (e.g., 100).

2. **Extreme Rating Ratio Analysis**:
   - Detects abnormal patterns of extremely low (`score ≤ 1`) or high (`score ≥ 4`) ratings.
   - If more than 60% of recent ratings fall into these categories, the system flags them as unverified.

3. **Verified vs. Unverified Ratings**:
   - Verified ratings are considered reliable and are included in the content's cached average rating.
   - Unverified ratings are excluded until they can be manually reviewed.

4. **Caching for Performance**:
   - Uses Redis to track recent rating activity and minimize database queries.
   - Ensures the spam detection system is efficient even under high traffic.

This mechanism ensures the integrity of the rating system by mitigating spam or manipulation attempts without affecting genuine user experiences.

## Tech Stack
- Django 4.2+
- Django REST Framework
- PostgreSQL
- Redis
- Docker

## Local Development Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Redis

### Installation
1. Clone the repository
```bash
git clone https://github.com/mostafa20001379/bitpin.git
cd bitpin
git checkout master
```

2. Run the projcet 
```bash
docker compose up -d --build
```