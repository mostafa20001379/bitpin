import {check} from 'k6';
import http from 'k6/http';
import {sleep} from 'k6';

// Define options for load and spam tests
export let options = {
    stages: [
        {duration: '1m', target: 50},   // Ramp up to 50 users over 1 minute
        {duration: '2m', target: 200},  // Ramp up to 200 users over 2 minutes
        {duration: '3m', target: 500},  // Ramp up to 500 users over 3 minutes
        {duration: '2m', target: 500},  // Maintain 500 users for 2 minutes
        {duration: '1m', target: 0},    // Ramp down to 0 users over 1 minute
    ],
    thresholds: {
        http_req_failed: ['rate<0.01'],  // Allow less than 1% of requests to fail
        http_req_duration: ['p(95)<2000'], // 95% of requests should complete in under 2 seconds
    },
};

// Simulate general load test with viewing and rating content
export default function () {
    // Simulate GET request to the Content endpoint (viewing content)
    let res = http.get('http://web:8000/api/contents/');
    check(res, {
        'is status 200': (r) => r.status === 200,
    });

    // Simulate POST request to the Rating endpoint (rating content)
    let contentId = 1; // Use an existing content ID in your DB
    let payload = JSON.stringify({score: 4});
    let params = {headers: {'Content-Type': 'application/json'}};
    res = http.post(`http://web:8000/api/contents/${contentId}/ratings/`, payload, params);
    check(res, {
        'is status 201': (r) => r.status === 201,
    });

    // Sleep to simulate user think time
    sleep(1);
}

// Spam Test: Multiple ratings from the same user for the same content
export function spamTest() {
    // Content ID and user setup
    let contentId = 1; // Target content ID for spam ratings
    let payload = JSON.stringify({score: 5});
    let params = {headers: {'Content-Type': 'application/json'}};

    // Simulate 50 POST requests for the same content to test spam detection
    for (let i = 0; i < 50; i++) {
        let res = http.post(`http://web:8000/api/contents/${contentId}/ratings/`, payload, params);
        check(res, {
            'is status 201': (r) => r.status === 201,
        });

        // Short delay between spam requests (to simulate user input but still "spam")
        sleep(0.1);
    }
}
