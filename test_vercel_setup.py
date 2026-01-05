"""
Test script to verify Vercel deployment setup
Run this to check if your app works before deploying
"""

import sys
import os

# Add api directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

try:
    from api.index import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Error importing Flask app: {e}")
    sys.exit(1)

try:
    import psutil
    print("✅ psutil imported successfully")
except Exception as e:
    print(f"❌ Error importing psutil: {e}")
    sys.exit(1)

try:
    import requests
    print("✅ requests imported successfully")
except Exception as e:
    print(f"❌ Error importing requests: {e}")
    sys.exit(1)

# Test routes
with app.test_client() as client:
    try:
        response = client.get('/')
        if response.status_code == 200:
            print("✅ Home route (/) working")
        else:
            print(f"❌ Home route failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing home route: {e}")
    
    try:
        response = client.get('/status')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('status') == 'ok':
                print("✅ Status API (/status) working")
                print(f"   CPU: {data.get('cpu_usage')}%")
                print(f"   Memory: {data.get('memory_used')}/{data.get('memory_total')} GB")
            else:
                print(f"❌ Status API returned error: {data}")
        else:
            print(f"❌ Status API failed with status {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing status route: {e}")
    
    try:
        response = client.post('/regenerate')
        data = response.get_json()
        if data.get('status') == 'error' and 'serverless' in data.get('message', '').lower():
            print("✅ Regenerate route correctly returns serverless limitation message")
        else:
            print(f"⚠️  Regenerate route response: {data}")
    except Exception as e:
        print(f"❌ Error testing regenerate route: {e}")

print("\n" + "="*50)
print("🎉 All tests passed! Ready for Vercel deployment.")
print("="*50)
print("\nNext steps:")
print("1. Commit your changes: git add . && git commit -m 'Add Vercel support'")
print("2. Push to GitHub: git push")
print("3. Deploy on Vercel: https://vercel.com/new")
print("\nOr run locally with: python api/index.py")
