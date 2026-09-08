import { expect, test } from './fixtures';

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

test('dismisses a completed goal across reloads and shows it when resumed', async ({
  page,
}) => {
  await page.clock.install();
  let completed = true;
  await page.route('**/sessionData/fixture-active', async (route) => {
    const response = await route.fetch();
    const body: unknown = await response.json();
    if (!isRecord(body) || !isRecord(body.session))
      throw new Error('The fixture has no session');
    await route.fulfill({
      response,
      json: {
        ...body,
        session: {
          ...body.session,
          goal: {
            objective: 'Completed goal marker',
            state: completed ? 'completed' : 'active',
            completed,
            reason: null,
          },
        },
      },
    });
  });

  await page.goto('/#/s/fixture-active');
  await expect(page.getByText('Completed goal marker')).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Dismiss completed goal' }),
  ).toHaveText('✕');
  await page.getByRole('button', { name: 'Dismiss completed goal' }).click();
  await expect(page.getByText('Completed goal marker')).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Confirm dismiss completed goal' }),
  ).toHaveText('hide?');
  await page.clock.fastForward(4_000);
  await expect(
    page.getByRole('button', { name: 'Dismiss completed goal' }),
  ).toHaveText('✕');
  await page.getByRole('button', { name: 'Dismiss completed goal' }).click();
  await page
    .getByRole('button', { name: 'Confirm dismiss completed goal' })
    .click();
  await expect(page.getByText('Completed goal marker')).toHaveCount(0);
  await page.reload();
  await expect(page.locator('.stream')).toBeVisible();
  await expect(page.getByText('Completed goal marker')).toHaveCount(0);

  completed = false;
  await page.reload();
  await expect(page.getByText('Completed goal marker')).toBeVisible();
  await expect(
    page.getByRole('button', { name: 'Dismiss completed goal' }),
  ).toHaveCount(0);
  completed = true;
  await page.reload();
  await expect(
    page.getByRole('button', { name: 'Dismiss completed goal' }),
  ).toBeVisible();
});
