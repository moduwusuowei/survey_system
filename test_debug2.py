"""
Playwright E2E 测试脚本 - 问卷系统
诊断版本 - 检查前端数据
"""
from playwright.sync_api import sync_playwright


def test_survey_list():
    """测试问卷列表页面"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
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

            # 检查每行的详细 HTML
            print("\n2. 检查行的 HTML 结构...")
            rows = page.locator(".el-table__body-wrapper tr")
            for i in range(min(rows.count(), 3)):
                row = rows.nth(i)
                row_html = row.inner_html()
                print(f"\n   行 {i+1} HTML:")
                print(f"   {row_html}")

            # 打印表格的所有文本内容
            print("\n3. 表格状态列...")
            status_col = page.locator(".el-table__body-wrapper td:nth-child(4)")
            for i in range(status_col.count()):
                text = status_col.nth(i).text_content()
                print(f"   状态列 {i+1}: '{text.strip()}'")

            # 检查操作列的按钮
            print("\n4. 操作列按钮...")
            action_col = page.locator(".el-table__body-wrapper td:nth-child(8)")
            for i in range(min(action_col.count(), 3)):
                buttons = action_col.nth(i).locator("button")
                btn_texts = [buttons.nth(j).text_content().strip() for j in range(buttons.count())]
                print(f"   行 {i+1} 按钮: {btn_texts}")

            print("\n" + "="*50)
            print("诊断完成")
            print("="*50)

        except Exception as e:
            print(f"\n❌ 异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("test_output", exist_ok=True)
    test_survey_list()
