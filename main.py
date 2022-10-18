#! /usr/bin/env python3

import argparse
import datetime
from tasker import Tasker


def main() -> None:
    tasker = Tasker()
    parser = argparse.ArgumentParser(description="Handle pending tasks")
    parser.add_argument("-t", "--task", help="Name of the task to handle")
    parser.add_argument(
        "-p",
        "--priority",
        type=int,
        help="Priority of the task.\n0: Highest priority",
    )
    parser.add_argument(
        "-dl",
        "--deadline",
        type=int,
        help="Number of days before the due date.\n"
        "Cannot be used with the -d argument.",
    )
    parser.add_argument(
        "-d",
        "--date",
        help="Due date in ISO format (\033[3me.g.\033[0m 2022-12-25)\n"
        "Cannot be used with the -dl argument",
    )
    parser.add_argument(
        "-c", "--create", action="store_true", help="Create a new task"
    )
    parser.add_argument(
        "-f",
        "--finish",
        action="store_true",
        help="Finishes a pending task.\n"
        "If no task is passed, the current one is assumed",
    )
    parser.add_argument(
        "-e", "--edit", action="store_true", help="Edit a task"
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Show the current pending task",
    )
    parser.add_argument(
        "-a",
        "--show-all",
        action="store_true",
        help="Show all the tasks, in order of urgency",
    )
    parser.add_argument(
        "-r",
        "--reset",
        action="store_true",
        help="Reset all the pending tasks",
    )

    args = parser.parse_args()
    if args.create:
        name = args.task
        if name is None:
            name = args.create
            if name is None:
                print("No name for task")
                exit(1)
        priority = args.priority
        if priority is None:
            print(f"No given priority for {name}")
            exit(1)
        due_date = args.date
        deadline = args.deadline
        d = deadline if deadline is not None else due_date
        if due_date is None and deadline is None:
            print(f"No deadline for task {name}")
            exit(1)
        elif ((due_date is not None) and (deadline is not None)) and (
            datetime.date.fromisoformat(due_date) - datetime.date.today()
        ).days != deadline:
            print("Two different deadlines given")
            exit(1)
        try:
            tasker.create(name, priority, d)
        except ValueError as e:
            print(f"Error: {e}")
    elif args.finish:
        if args.task is None:
            if tasker.current_task is None:
                print("No current task")
                exit(1)
            while (
                res := input(
                    f"Finished current task {tasker.current_task}? [y/N]\n"
                )
            ) not in {"y", "N"}:
                pass
            if res == "y":
                tasker.finish(tasker.current_task.name)
                print("✨ Congrats ✨")
            else:
                pass
        else:
            try:
                tasker.finish(args.task)
            except ValueError:
                print(f"No task {args.task}")
    elif args.edit:
        if args.task is None:
            print("No task given to edit")
            exit(1)
        elif args.task not in tasker.task_names():
            print(f"No such task: {args.task}")
            exit(1)
        else:
            _prio = args.priority
            _t = tasker.get_task_by_name(args.task)
            if _prio is not None:
                try:
                    _t.priority = _prio
                except ValueError as e:
                    print(f"Warning: {e}, skipping priority edit")
            _dl = args.deadline
            _dd = args.date
            if _dl is not None and _dd is not None:
                print(
                    f"Warning, two dates given for {args.task}, "
                    f"skipping deadline edit"
                )
            elif (_dl is not None) ^ (_dd is not None):
                _d = _dl if _dl is not None else _dd
                try:
                    _t.deadline = _d
                except ValueError as e:
                    print(f"Warning: {e}, skipping deadline edit")
            else:
                pass
            tasker.save()
    elif args.reset:
        while (
            res := input(
                "Are you sure to reset all the pending tasks? [y/N]\n"
            )
        ) not in {"y", "N"}:
            pass
        if res == "y":
            tasker.reset()
            print("Tasks cleared")

    if args.show:
        task = tasker.current_task
        if task is not None:
            print(task)
        else:
            print("No current task")
    elif args.show_all:
        all_tasks = tasker.get_all_tasks()
        print_last = True
        for _task, _prio, _deadline in all_tasks:
            print_last = False
            print(
                f"{_task} [{_prio}]: {_deadline} "
                f"day{'s' if _deadline > 1 else ''} remaining"
            )
        else:
            if print_last:
                print("No pending tasks")


if __name__ == "__main__":
    main()
