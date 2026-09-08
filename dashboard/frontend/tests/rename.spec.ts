import { expect, test } from './fixtures';

for (const automatic of [false, true]) {
  test(`shows progress and completion for ${automatic ? 'automatic' : 'manual'} rename`, async ({
    page,
  }) => {
    let release: () => void = () => {
      throw new Error('The request gate is not ready');
    };
    const pending = new Promise<void>((resolve) => {
      release = resolve;
    });
    let requests = 0;
    await page.route('**/controls/*', async (route) => {
      requests += 1;
      expect(route.request().url()).toContain(
        automatic ? '/auto-name-session' : '/rename-session',
      );
      await pending;
      await route.fulfill({
        json: {
          request_id: 'rename-test',
          status: 'acknowledged',
          reason: null,
        },
      });
    });
    await page.goto('/#/s/fixture-active');
    await page.getByRole('button', { name: '✎ rename', exact: true }).click();
    const input = page.getByRole('textbox', {
      name: 'session name',
      exact: true,
    });
    const title = await input.inputValue();
    if (!automatic) await input.fill('New session name');
    const form = page.locator('.rename-menu');
    await form
      .getByRole('button', {
        name: automatic ? 'automatic' : 'rename',
        exact: true,
      })
      .click();
    const status = page.getByRole('status', { name: 'rename status' });
    await expect(status).toContainText(
      automatic ? 'Creating and applying' : 'Renaming to',
    );
    await expect(
      page.getByRole('button', { name: '⏳ renaming…', exact: true }),
    ).toBeDisabled();
    await expect(input).toBeDisabled();
    for (const button of await form.getByRole('button').all())
      await expect(button).toBeDisabled();
    expect(requests).toBe(1);
    release();
    await expect(status).toContainText(
      automatic
        ? `Rename complete. Current name: “${title}”.`
        : 'Renamed to “New session name”.',
    );
    await expect(form).toHaveCount(0);
    await expect(
      page.getByRole('button', { name: '✎ rename', exact: true }),
    ).toBeEnabled();
  });
}

for (const outcome of ['rejected', 'indeterminate', 'network']) {
  test(`keeps the rename draft after ${outcome} and allows a retry`, async ({
    page,
  }) => {
    await page.route('**/controls/rename-session', async (route) => {
      if (outcome === 'network') await route.abort();
      else
        await route.fulfill({
          status: outcome === 'rejected' ? 409 : 202,
          json: {
            request_id: 'rename-test',
            status: outcome,
            reason: 'Title was not confirmed',
          },
        });
    });
    await page.goto('/#/s/fixture-active');
    await page.getByRole('button', { name: '✎ rename', exact: true }).click();
    const input = page.getByRole('textbox', {
      name: 'session name',
      exact: true,
    });
    await input.fill('Keep this name');
    const submit = page
      .locator('.rename-menu')
      .getByRole('button', { name: 'rename', exact: true });
    await submit.click();
    await expect(page.locator('.action-failure')).toBeVisible();
    if (outcome !== 'network')
      await expect(page.locator('.action-failure')).toHaveText(
        'Title was not confirmed',
      );
    await expect(input).toHaveValue('Keep this name');
    await expect(submit).toBeEnabled();
    await expect(
      page.getByRole('status', { name: 'rename status', includeHidden: true }),
    ).not.toContainText('Rename complete');
  });
}
