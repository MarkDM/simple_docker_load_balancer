import requests
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def send_request(request_num, url):
    """Send a single HTTP GET request and return the result."""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        elapsed = time.time() - start_time
        return {
            'request': request_num,
            'status': response.status_code,
            'time': elapsed,
            'success': True,
            'content': response.text[:100]  # First 100 chars
        }
    except Exception as e:
        return {
            'request': request_num,
            'status': None,
            'time': None,
            'success': False,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='Send multiple HTTP requests to localhost:80')
    parser.add_argument('-n', '--number', type=int, default=1000,
                        help='Number of requests to send (default: 1000)')
    parser.add_argument('-c', '--concurrent', type=int, default=1,
                        help='Number of concurrent requests (default: 1)')
    parser.add_argument('-u', '--url', type=str, default='http://localhost:80',
                        help='URL to send requests to (default: http://localhost:80)')
    
    args = parser.parse_args()
    
    print(f"Sending {args.number} requests to {args.url}")
    print(f"Concurrency: {args.concurrent}")
    print("-" * 60)
    
    results = []
    start_time = time.time()
    
    # Use ThreadPoolExecutor for concurrent requests
    with ThreadPoolExecutor(max_workers=args.concurrent) as executor:
        futures = [executor.submit(send_request, i+1, args.url) 
                   for i in range(args.number)]
        
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            
            if result['success']:
                print(f"Request {result['request']}: "
                      f"Status {result['status']}, "
                      f"Time: {result['time']:.3f}s")
            else:
                print(f"Request {result['request']}: FAILED - {result['error']}")
    
    total_time = time.time() - start_time
    
    # Print summary
    print("-" * 60)
    successful = sum(1 for r in results if r['success'])
    failed = len(results) - successful
    
    if successful > 0:
        avg_time = sum(r['time'] for r in results if r['success']) / successful
        print(f"Total requests: {args.number}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Average response time: {avg_time:.3f}s")
        print(f"Total time: {total_time:.3f}s")
        print(f"Requests per second: {args.number / total_time:.2f}")
    else:
        print(f"All {args.number} requests failed!")

if __name__ == '__main__':
    main()
