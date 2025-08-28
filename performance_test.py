#!/usr/bin/env python3
"""
Performance Testing Script for Karnataka Village Visualization
This script measures loading times and helps optimize performance.
"""

import time
import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_api_endpoints():
    """Test API endpoints and measure response times"""
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/",
        "/api/data",
        "/api/districts",
        "/api/villages"
    ]
    
    print("🧪 Testing API endpoints...")
    print("=" * 50)
    
    results = {}
    
    for endpoint in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            status = response.status_code
            
            results[endpoint] = {
                'status': status,
                'response_time_ms': response_time,
                'success': status == 200
            }
            
            print(f"✅ {endpoint}: {status} ({response_time:.1f}ms)")
            
        except requests.exceptions.RequestException as e:
            results[endpoint] = {
                'status': 'ERROR',
                'response_time_ms': None,
                'success': False,
                'error': str(e)
            }
            print(f"❌ {endpoint}: ERROR - {str(e)}")
    
    return results

def test_data_loading_performance():
    """Test data loading performance"""
    
    print("\n📊 Testing data loading performance...")
    print("=" * 50)
    
    try:
        # Test main data endpoint
        start_time = time.time()
        response = requests.get("http://localhost:8000/api/data", timeout=60)
        end_time = time.time()
        
        if response.status_code == 200:
            data = response.json()
            load_time = (end_time - start_time) * 1000
            
            print(f"✅ Data loaded in {load_time:.1f}ms")
            print(f"📈 Village count: {data.get('village_count', 'Unknown')}")
            print(f"📊 Population stats: {data.get('population_stats', {})}")
            
            # Check if loading time meets requirement (< 10 seconds)
            if load_time < 10000:
                print("🎯 Performance target met: < 10 seconds")
            else:
                print(f"⚠️ Performance target exceeded: {load_time/1000:.1f}s")
            
            return load_time
        else:
            print(f"❌ Failed to load data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing data loading: {str(e)}")
        return None

def test_concurrent_requests():
    """Test concurrent request handling"""
    
    print("\n🔄 Testing concurrent request handling...")
    print("=" * 50)
    
    def make_request(request_id):
        try:
            start_time = time.time()
            response = requests.get("http://localhost:8000/api/villages?limit=10", timeout=30)
            end_time = time.time()
            
            return {
                'id': request_id,
                'success': response.status_code == 200,
                'response_time': (end_time - start_time) * 1000,
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'id': request_id,
                'success': False,
                'response_time': None,
                'error': str(e)
            }
    
    # Test with 10 concurrent requests
    concurrent_requests = 10
    print(f"Testing {concurrent_requests} concurrent requests...")
    
    start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(make_request, i) for i in range(concurrent_requests)]
        results = [future.result() for future in as_completed(futures)]
    
    total_time = (time.time() - start_time) * 1000
    
    successful_requests = sum(1 for r in results if r['success'])
    avg_response_time = sum(r['response_time'] for r in results if r['response_time']) / len([r for r in results if r['response_time']])
    
    print(f"✅ Concurrent test completed in {total_time:.1f}ms")
    print(f"📊 Successful requests: {successful_requests}/{concurrent_requests}")
    print(f"⏱️ Average response time: {avg_response_time:.1f}ms")
    
    return results

def generate_performance_report(results, data_load_time, concurrent_results):
    """Generate a comprehensive performance report"""
    
    print("\n📋 Performance Report")
    print("=" * 50)
    
    # API Endpoints
    print("\n🔗 API Endpoints:")
    for endpoint, result in results.items():
        status_icon = "✅" if result['success'] else "❌"
        time_info = f"{result['response_time_ms']:.1f}ms" if result['response_time_ms'] else "ERROR"
        print(f"   {status_icon} {endpoint}: {time_info}")
    
    # Data Loading
    if data_load_time:
        print(f"\n📊 Data Loading Performance:")
        print(f"   ⏱️ Load time: {data_load_time:.1f}ms")
        if data_load_time < 10000:
            print("   🎯 Target met: < 10 seconds")
        else:
            print(f"   ⚠️ Target exceeded: {data_load_time/1000:.1f}s")
    
    # Concurrent Performance
    if concurrent_results:
        successful = sum(1 for r in concurrent_results if r['success'])
        total = len(concurrent_results)
        avg_time = sum(r['response_time'] for r in concurrent_results if r['response_time']) / len([r for r in concurrent_results if r['response_time']])
        
        print(f"\n🔄 Concurrent Request Performance:")
        print(f"   📊 Success rate: {successful}/{total} ({successful/total*100:.1f}%)")
        print(f"   ⏱️ Average response time: {avg_time:.1f}ms")
    
    # Recommendations
    print(f"\n💡 Performance Recommendations:")
    if data_load_time and data_load_time > 5000:
        print("   • Consider implementing data caching")
        print("   • Optimize geometry simplification")
        print("   • Use progressive loading for large datasets")
    
    if concurrent_results:
        success_rate = sum(1 for r in concurrent_results if r['success']) / len(concurrent_results)
        if success_rate < 0.9:
            print("   • Improve concurrent request handling")
            print("   • Consider request queuing for heavy loads")
    
    print("   • Monitor memory usage during peak loads")
    print("   • Implement request rate limiting if needed")

def main():
    """Main performance testing function"""
    
    print("🚀 Karnataka Village Visualization - Performance Test")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running at http://localhost:8000")
        else:
            print("⚠️ Server responded with unexpected status")
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the application first:")
        print("   python main.py")
        return
    
    # Run performance tests
    try:
        # Test API endpoints
        api_results = test_api_endpoints()
        
        # Test data loading
        data_load_time = test_data_loading_performance()
        
        # Test concurrent requests
        concurrent_results = test_concurrent_requests()
        
        # Generate report
        generate_performance_report(api_results, data_load_time, concurrent_results)
        
    except KeyboardInterrupt:
        print("\n⏹️ Performance testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during performance testing: {str(e)}")
    
    print("\n🎯 Performance testing completed!")

if __name__ == "__main__":
    main()
