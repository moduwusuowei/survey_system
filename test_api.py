"""测试问卷系统 API"""
import requests
import json

BASE_URL = "http://localhost:9999/api/v1"

def test_api():
    print("测试问卷系统 API")
    print("="*50)

    # 1. 登录
    print("\n1. 测试登录...")
    login_data = {
        "email": "admin@example.com",
        "password": "12345678"
    }
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            token = data.get("data", {}).get("access_token")
            print(f"   ✓ 登录成功，获取到 token")
            headers = {"Authorization": f"Bearer {token}"}

            # 2. 获取问卷列表
            print("\n2. 测试获取问卷列表...")
            resp = requests.get(f"{BASE_URL}/questionnaires/", headers=headers)
            print(f"   状态码: {resp.status_code}")
            if resp.status_code == 200:
                surveys = resp.json()
                if isinstance(surveys, dict):
                    surveys = surveys.get("data", [])
                print(f"   ✓ 问卷数量: {len(surveys)}")
                for s in surveys:
                    print(f"    - ID:{s.get('id')} {s.get('title')} ({s.get('status')})")
            else:
                print(f"   响应: {resp.text[:200]}")

            # 3. 获取单个问卷
            if surveys:
                survey_id = surveys[0].get("id")
                print(f"\n3. 测试获取问卷 {survey_id}...")
                resp = requests.get(f"{BASE_URL}/questionnaires/{survey_id}", headers=headers)
                print(f"   状态码: {resp.status_code}")
                if resp.status_code == 200:
                    print(f"   ✓ 获取问卷成功")
                else:
                    print(f"   响应: {resp.text[:200]}")

        else:
            print(f"   响应: {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    test_api()
