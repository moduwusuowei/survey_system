"""检查问卷的 end_date 状态"""
import requests

BASE_URL = "http://localhost:9999/api/v1"

# 登录
login_data = {"email": "admin@example.com", "password": "12345678"}
resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
token = resp.json()["data"]["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 获取问卷列表
resp = requests.get(f"{BASE_URL}/questionnaires/", headers=headers)
surveys = resp.json()

if isinstance(surveys, dict):
    surveys = surveys.get("data", [])

from datetime import datetime, timezone

print("问卷状态检查:")
print("="*60)
for s in surveys:
    status = s.get("status")
    end_date = s.get("end_date")
    title = s.get("title")

    if end_date:
        # 解析 ISO 格式日期
        if end_date.endswith('Z'):
            end_date = end_date[:-1] + '+00:00'
        end_dt = datetime.fromisoformat(end_date)
        # 确保 end_dt 是 aware datetime
        if end_dt.tzinfo is None:
            end_dt = end_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        is_expired = end_dt < now
        expired_str = "已过期" if is_expired else "未过期"
    else:
        expired_str = "无结束日期"

    print(f"ID:{s.get('id'):2} | {status:10} | {expired_str:10} | {title}")
    if end_date:
        print(f"         end_date: {end_date}")

print("="*60)
