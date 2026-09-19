# Testing Summary

## Integration Testing
Ran `pytest tests/test_integration.py -v` against the live Docker Compose stack.

## Load Testing
Sent 100 concurrent requests to `/api/v1/predict` using `load_test.py`.

### Results Before Fix
- Successes: 100/100
- Sequential baseline latency: ~31 ms
- Concurrent average latency: ~437 ms

### Bug Found
The `/predict` endpoint was a synchronous route, causing concurrent requests to compete for the available thread pool.

### Fix Applied
Added `--workers 4` to the Uvicorn startup command in the Dockerfile.

### Results After Fix
- Total requests: 100
- Successes: 100
- Failures: 0
- Total wall time: 5.01 s
- Average response time: 3593.0 ms
- Minimum response time: 1014.9 ms
- Maximum response time: 4947.5 ms

### Verification
Confirmed that Uvicorn started 4 worker processes and the model was loaded once by each worker.

### Conclusion
The API processed all 100 requests successfully with zero failures. However, the measured average latency after applying the 4-worker configuration was higher than the earlier test result, so the performance improvement was not confirmed by this test run.