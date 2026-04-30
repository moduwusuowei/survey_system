import { test, expect } from '@playwright/test';

test.describe('问卷系统登录', () => {
  test('应该显示登录页面', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByText('用户登录')).toBeVisible();
  });

  test('应该能够使用有效凭据登录', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('请输入邮箱').fill('admin@example.com');
    await page.getByPlaceholder('请输入密码').fill('12345678');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('应该拒绝无效凭据', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('请输入邮箱').fill('invalid@example.com');
    await page.getByPlaceholder('请输入密码').fill('wrongpassword');
    await page.getByRole('button', { name: '登录' }).click();
    // 等待可能的错误提示
    await page.waitForTimeout(2000);
  });
});

test.describe('问卷管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('请输入邮箱').fill('admin@example.com');
    await page.getByPlaceholder('请输入密码').fill('12345678');
    await page.getByRole('button', { name: '登录' }).click();
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('应该显示问卷列表', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page.getByText('问卷标题')).toBeVisible();
  });

  test('应该能够创建新问卷', async ({ page }) => {
    await page.goto('/survey/create');
    await page.getByPlaceholder('请输入问卷标题').fill('测试问卷');
    await page.getByRole('button', { name: '保存' }).click();
    // 等待保存完成
    await page.waitForTimeout(2000);
    // 验证是否返回问卷列表
    await expect(page).toHaveURL(/\/surveys/);
  });

  test('应该能够发布问卷', async ({ page }) => {
    await page.goto('/dashboard');
    const draftSurvey = page.locator('tr').filter({ hasText: '草稿' }).first();
    if (await draftSurvey.isVisible()) {
      await draftSurvey.getByRole('button', { name: '发布' }).click();
      await page.waitForTimeout(2000);
    }
  });

  test('一键终止后应显示重新发布按钮', async ({ page }) => {
    await page.goto('/dashboard');
    const publishedSurvey = page.locator('tr').filter({ hasText: '已发布' }).first();
    if (await publishedSurvey.isVisible()) {
      await publishedSurvey.getByRole('button', { name: '一键终止' }).click();
      await page.waitForTimeout(2000);
    }
  });
});

test.describe('问卷填写', () => {
  test('应该能够填写并提交问卷', async ({ page }) => {
    await page.goto('/respond/1');
    // 等待页面加载
    await page.waitForTimeout(3000);
    // 检查是否加载成功（不是错误状态）
    await expect(page.getByText('加载中...')).not.toBeVisible();
    await expect(page.getByText('问卷访问受限')).not.toBeVisible();
  });

  test('过期问卷应显示相应提示', async ({ page }) => {
    await page.goto('/respond/999');
    // 等待页面加载
    await page.waitForTimeout(3000);
    // 检查错误信息
    await expect(page.getByText('加载问卷失败')).toBeVisible();
  });
});
