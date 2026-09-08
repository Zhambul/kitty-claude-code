import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { translateSession } from '../../api/translators/session-data';
import { wireSession } from '../../test/session-fixture';
import type { Session } from '../model';
import GoalTasks from './GoalTasks.svelte';

function completedGoal(id = 'session-one', objective = 'Ship it'): Session {
  return {
    ...translateSession(wireSession(id)),
    goal: { objective, state: 'completed', completed: true, reason: null },
  };
}

describe('completed goal dismissal', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it('keeps the goal dismissed after the view opens again', async () => {
    const view = render(GoalTasks, { session: completedGoal() });
    await userEvent.click(
      screen.getByRole('button', { name: 'Dismiss completed goal' }),
    );
    expect(screen.queryByText('Ship it')).not.toBeInTheDocument();
    expect(screen.getByText('Rewrite')).toBeInTheDocument();
    view.unmount();
    render(GoalTasks, { session: completedGoal() });
    expect(screen.queryByText('Ship it')).not.toBeInTheDocument();
  });

  it('shows a different goal and keeps other sessions separate', async () => {
    const view = render(GoalTasks, { session: completedGoal() });
    await userEvent.click(
      screen.getByRole('button', { name: 'Dismiss completed goal' }),
    );
    await view.rerender({ session: completedGoal('session-two') });
    expect(screen.getByText('Ship it')).toBeInTheDocument();
    await view.rerender({ session: completedGoal('session-one', 'Next goal') });
    expect(screen.getByText('Next goal')).toBeInTheDocument();
    await view.rerender({ session: completedGoal() });
    expect(screen.getByText('Ship it')).toBeInTheDocument();
  });

  it('shows a resumed goal and allows a later dismissal', async () => {
    const view = render(GoalTasks, { session: completedGoal() });
    await userEvent.click(
      screen.getByRole('button', { name: 'Dismiss completed goal' }),
    );
    await view.rerender({ session: translateSession(wireSession()) });
    expect(screen.getByText('Ship it')).toBeInTheDocument();
    expect(
      screen.queryByRole('button', { name: 'Dismiss completed goal' }),
    ).not.toBeInTheDocument();
    await view.rerender({ session: completedGoal() });
    expect(
      screen.getByRole('button', { name: 'Dismiss completed goal' }),
    ).toBeInTheDocument();
  });

  it('dismisses the current card if storage is blocked', async () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
      throw new Error('Storage is blocked');
    });
    render(GoalTasks, { session: completedGoal() });
    await userEvent.click(
      screen.getByRole('button', { name: 'Dismiss completed goal' }),
    );
    expect(screen.queryByText('Ship it')).not.toBeInTheDocument();
  });
});
