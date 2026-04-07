"""
Habit bot commands — registered via the msgio command registry.
Imported automatically by msgio.commands.load_app_commands() on startup.
"""

from datetime import date

from django.utils.translation import gettext as _

from moodyduck.msgio.commands import register_command, reply


@register_command("/habit")
def cmd_habit(user, gateway, sender_id, args):
    from moodyduck.habits.models import Habit, HabitLog

    if user is None:
        reply(
            gateway,
            sender_id,
            _(
                "Not linked. Generate a pairing token in your MoodyDuck profile and send /start <token>."
            ),
        )
        return

    habit_name = args.strip()
    if not habit_name:
        habits = Habit.objects.filter(user=user)
        listing = "\n".join(f"  • {h.name}" for h in habits) or _(
            "  (no habits defined yet)"
        )
        reply(
            gateway,
            sender_id,
            _("Usage: /habit <name>\n\nYour habits:\n{listing}").format(
                listing=listing
            ),
        )
        return

    habit = Habit.objects.filter(user=user, name__iexact=habit_name).first()
    if not habit:
        habits = Habit.objects.filter(user=user)
        listing = ", ".join(h.name for h in habits) or _("none")
        reply(
            gateway,
            sender_id,
            _("❌ Habit '{name}' not found.\nYour habits: {listing}").format(
                name=habit_name, listing=listing
            ),
        )
        return

    HabitLog.objects.create(habit=habit, date=date.today())
    reply(gateway, sender_id, _("✅ Logged habit: {name}").format(name=habit.name))
