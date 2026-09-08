<script lang="ts">
  import type { Session } from '../model';

  let { session }: { session: Session } = $props();
  let dismissedObjective = $state<string | null>(null);
  const storageKey = $derived(`baqylau.dismissed-goal.${session.sessionId}`);

  $effect(() => {
    const goal = session.goal;
    try {
      if (
        !goal?.completed ||
        localStorage.getItem(storageKey) !== goal.objective
      )
        localStorage.removeItem(storageKey);
      dismissedObjective = localStorage.getItem(storageKey);
    } catch {
      // The card still works when browser storage is not available.
      dismissedObjective = null;
    }
  });

  function dismissGoal(): void {
    if (!session.goal?.completed || !session.goal.objective) return;
    dismissedObjective = session.goal.objective;
    try {
      localStorage.setItem(storageKey, dismissedObjective);
    } catch {
      // Keep this dismissal for the current view.
    }
  }

  function goalMark(state: NonNullable<Session['goal']>['state']): string {
    switch (state) {
      case 'completed':
        return '✓';
      case 'blocked':
      case 'usage_limited':
      case 'budget_limited':
        return '!';
      case 'paused':
        return 'Ⅱ';
      case 'cleared':
        return '−';
      case 'active':
        return '◎';
    }
  }

  function goalLabel(state: NonNullable<Session['goal']>['state']): string {
    if (state === 'completed') return 'achieved';
    return state.replace('_', ' ');
  }

  function taskClass(state: Session['tasks'][number]['state']): string {
    switch (state) {
      case 'pending':
        return 'pend';
      case 'in_progress':
        return 'active';
      case 'completed':
        return 'done';
      case 'deleted':
        return 'done';
    }
  }

  function taskMark(state: Session['tasks'][number]['state']): string {
    switch (state) {
      case 'pending':
        return '○';
      case 'in_progress':
        return '◉';
      case 'completed':
        return '✓';
      case 'deleted':
        return '−';
    }
  }
</script>

{#if session.goal?.objective && !(session.goal.completed && dismissedObjective === session.goal.objective)}
  <div class="goalwrap">
    <div class:met={session.goal.completed} class="goalcard">
      <div class="goalhead">
        <span class="goalmark">{goalMark(session.goal.state)}</span>
        <span class="goaltitle">goal</span>
        <span class="goalstate">{goalLabel(session.goal.state)}</span>
        {#if session.goal.completed}
          <button
            type="button"
            class="goal-dismiss"
            aria-label="Dismiss completed goal"
            onclick={dismissGoal}>dismiss</button
          >
        {/if}
      </div>
      <div class="goalcond">{session.goal.objective}</div>
      {#if session.goal.reason}
        <div class="goalreason">{session.goal.reason}</div>
      {/if}
    </div>
  </div>
{/if}

{#if session.tasks.length > 0}
  <div class="taskswrap">
    <div class="taskscard">
      <div class="taskshead">
        <span class="taskstitle">tasks</span>
        <span class="taskscount">{session.tasks.length}</span>
      </div>
      <div class="tasklist">
        {#each session.tasks as task (task.taskId)}
          <div class={['taskrow', taskClass(task.state)]}>
            <span class="taskmark">{taskMark(task.state)}</span>
            <span class="taskid">{task.taskId}</span>
            <span class="tasksubj">{task.subject}</span>
            {#if task.state === 'in_progress'}
              <span class="taskactive">active</span>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  </div>
{/if}

<style>
  .goal-dismiss {
    padding: 4px 8px;
    color: var(--text);
    background: transparent;
    border: 1px solid currentColor;
    border-radius: 4px;
    cursor: pointer;
    font: inherit;
  }
</style>
