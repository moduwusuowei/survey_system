"""
Playwright E2E 测试脚本 - 问卷系统
测试问卷管理页面功能 - 调试版本
"""
from playwright.sync_api import sync_playwright


def test_survey_list():
    """测试问卷列表页面"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # 登录
            print("1. 测试登录...")
            page.goto("http://localhost:5173/login")
            page.wait_for_load_state("networkidle")

            page.get_by_placeholder("请输入邮箱").fill("admin@example.com")
            page.get_by_placeholder("请输入密码").fill("12345678")
            page.get_by_role("button", name="登录").click()

            page.wait_for_url("**/dashboard", timeout=15000)
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            page.screenshot(path="test_output/01_login_dashboard.png", full_page=True)
            print("   ✓ 登录成功")

            # 检查表格结构
            print("\n2. 检查表格结构...")

            # 获取所有行
            rows = page.locator(".el-table__body-wrapper > table > tbody > tr")
            count = rows.count()
            print(f"   表格行数: {count}")

            # 打印每行的状态列内容
            for i in range(count):
                row = rows.nth(i)
                # 查找状态列 - 通常是第3列或带有 el-tag 的列
                status_cell = row.locator("td").nth(2)  # 第3列通常是状态列
                if status_cell.count() > 0:
                    status_text = status_cell.text_content()
                    print(f"   行 {i+1} 状态列: '{status_text.strip()}'")

                # 查找所有按钮
                buttons = row.locator("button")
                btn_count = buttons.count()
                btn_list = []
                for j in range(btn_count):
                    btn = buttons.nth(j)
                    btn_text = btn.text_content().strip()
                    btn_list.append(btn_text)
                print(f"   行 {i+1} 按钮: {btn_list}")

            # 检查 draft 行
            print("\n3. 查找 draft 行...")
            draft_row = page.locator(".el-table__body-wrapper tr").filter(has_text="draft").first
            if draft_row.count() > 0:
                print("   找到 draft 行")
                # 查找发布按钮
                publish_btn = draft_row.get_by_role("button", name="发布")
                print(f"   发布按钮数量: {publish_btn.count()}")

                # 尝试其他选择器
                all_buttons = draft_row.locator("button")
                print(f"   所有按钮:")
                for i in range(all_buttons.count()):
                    btn = all_buttons.nth(i)
                    print(f"    - text: '{btn.text_content().strip()}'")
            else:
                print("   未找到 draft 行")

            # 检查 published 行
            print("\n4. 查找 published 行...")
            pub_rows = page.locator(".el-table__body-wrapper tr").filter(has_text="published")
            pub_count = pub_rows.count()
            print(f"   published 行数量: {pub_count}")

            if pub_count > 0:
                pub = pub_rows.first
                # 检查按钮
                all_buttons = pub.locator("button")
                print(f"   published 行的按钮:")
                for i in range(all_buttons.count()):
                    btn = all_buttons.nth(i)
                    print(f"    - text: '{btn.text_content().strip()}'")

                # 查找一键终止按钮
                term_btn = pub.get_by_role("button", name="一键终止")
                print(f"   一键终止按钮数量: {term_btn.count()}")

            print("\n" + "="*50)
            print("调试完成")
            print("="*50)

        except Exception as e:
            print(f"\n❌ 异常: {e}")
            page.screenshot(path="test_output/error.png", full_page=True)
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("test_output", exist_ok=True)
    test_survey_list()
