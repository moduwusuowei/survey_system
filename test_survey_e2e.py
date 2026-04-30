"""
Playwright E2E 测试脚本 - 问卷系统
测试问卷管理页面功能
"""
from playwright.sync_api import sync_playwright


def test_survey_list():
    """测试问卷列表页面"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        console_messages = []
        page.on("console", lambda msg: console_messages.append(f"[{msg.type}] {msg.text}"))

        try:
            # ==================== 1. 登录 ====================
            print("1. 测试登录功能...")
            page.goto("http://localhost:5173/login")
            page.wait_for_load_state("networkidle")
            page.screenshot(path="test_output/01_login.png", full_page=True)

            page.get_by_placeholder("请输入邮箱").fill("admin@example.com")
            page.get_by_placeholder("请输入密码").fill("12345678")
            page.get_by_role("button", name="登录").click()

            page.wait_for_url("**/dashboard", timeout=15000)
            page.wait_for_load_state("networkidle")
            print("   ✓ 登录成功")

            # ==================== 2. 导航到问卷列表页面 ====================
            print("2. 导航到问卷列表页面...")
            page.goto("http://localhost:5173/surveys")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            page.screenshot(path="test_output/02_survey_list.png", full_page=True)
            print("   ✓ 进入问卷列表页面")

            # ==================== 3. 查看按钮状态 ====================
            print("\n3. 检查按钮显示状态...")

            rows = page.locator(".el-table__body-wrapper tr")
            count = rows.count()
            print(f"   表格行数: {count}")

            for i in range(count):
                row = rows.nth(i)
                buttons = row.locator("button")
                btn_list = [buttons.nth(j).text_content().strip() for j in range(buttons.count())]
                print(f"   行 {i+1} 按钮: {btn_list}")

            # ==================== 4. 测试发布 ====================
            print("\n4. 测试发布流程...")

            draft_rows = page.locator("tr").filter(has_text="draft")
            draft_count = draft_rows.count()
            print(f"   draft 状态问卷数量: {draft_count}")

            if draft_count > 0:
                draft = draft_rows.first
                publish_btn = draft.get_by_role("button", name="发布")
                if publish_btn.count() > 0:
                    print("   点击'发布'按钮...")
                    publish_btn.first.click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="test_output/03_after_publish.png", full_page=True)
                    print("   ✓ 发布成功")

                    # 刷新页面
                    page.goto("http://localhost:5173/surveys")
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
                else:
                    print("   ⚠ 未找到'发布'按钮")
            else:
                print("   ⚠ 无 draft 问卷")

            # ==================== 5. 测试一键终止 ====================
            print("\n5. 测试一键终止...")

            pub_rows = page.locator("tr").filter(has_text="published")
            pub_count = pub_rows.count()
            print(f"   published 状态问卷数量: {pub_count}")

            if pub_count > 0:
                # 查找有一键终止按钮的行
                term_rows = page.locator("tr").filter(has_text="一键终止")
                term_count = term_rows.count()
                print(f"   有一键终止按钮的行: {term_count}")

                if term_count > 0:
                    term_rows.first.get_by_role("button", name="一键终止").click()
                    page.wait_for_timeout(3000)
                    page.screenshot(path="test_output/04_after_terminate.png", full_page=True)
                    print("   ✓ 一键终止点击成功")

                    # 刷新页面检查按钮变化
                    page.goto("http://localhost:5173/surveys")
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
                    page.screenshot(path="test_output/05_after_terminate_refresh.png", full_page=True)

                    repub_rows = page.locator("tr").filter(has_text="重新发布")
                    if repub_rows.count() > 0:
                        print("   ✓ 一键终止后正确显示'重新发布'按钮")
                    else:
                        print("   ⚠ 一键终止后未显示'重新发布'按钮")
                else:
                    print("   ⚠ 无'一键终止'按钮（所有问卷都已过期或无未过期问卷）")
                    # 检查是否有重新发布按钮
                    repub_rows = page.locator("tr").filter(has_text="重新发布")
                    print(f"   '重新发布'按钮行数: {repub_rows.count()}")
            else:
                print("   ⚠ 无 published 问卷")

            # ==================== 6. 测试重新发布 ====================
            print("\n6. 测试重新发布...")

            repub_rows = page.locator("tr").filter(has_text="重新发布")
            if repub_rows.count() > 0:
                repub_rows.first.get_by_role("button", name="重新发布").click()
                page.wait_for_timeout(3000)
                page.screenshot(path="test_output/06_after_republish.png", full_page=True)
                print("   ✓ 重新发布点击成功")

                # 验证
                page.goto("http://localhost:5173/surveys")
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(2000)

                term_rows = page.locator("tr").filter(has_text="一键终止")
                if term_rows.count() > 0:
                    print("   ✓ 重新发布后重新显示'一键终止'按钮")
                else:
                    print("   ⚠ 重新发布后未显示'一键终止'按钮")
            else:
                print("   ⚠ 无重新发布按钮")

            # 控制台错误检查
            errors = [m for m in console_messages if "error" in m.lower()]
            if errors:
                print("\n控制台错误:")
                for e in errors[-5:]:
                    print(f"  {e}")

            print("\n" + "="*50)
            print("测试完成！")
            print("="*50)

        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            page.screenshot(path="test_output/error.png", full_page=True)
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    import os
    os.makedirs("test_output", exist_ok=True)

    print("="*50)
    print("问卷系统 E2E 自动化测试")
    print("="*50)
    test_survey_list()
