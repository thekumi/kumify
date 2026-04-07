"""
Mood bot commands — registered via the msgio command registry.
Imported automatically by msgio.commands.load_app_commands() on startup.
"""

from django.utils.translation import gettext as _

from moodyduck.msgio.commands import register_command, reply


@register_command("/mood")
def cmd_mood(user, gateway, sender_id, args):
    from moodyduck.mood.models import Mood, Status

    if user is None:
        reply(
            gateway,
            sender_id,
            _(
                "Not linked. Generate a pairing token in your MoodyDuck profile and send /start <token>."
            ),
        )
        return

    parts = args.split(maxsplit=1)
    if not parts or not parts[0]:
        moods = Mood.objects.filter(user=user).order_by("value")
        listing = "\n".join(f"  {m.value} — {m.name}" for m in moods) or _(
            "  (no moods defined yet)"
        )
        reply(
            gateway,
            sender_id,
            _("Usage: /mood <name_or_value> [text]\n\nYour moods:\n{listing}").format(
                listing=listing
            ),
        )
        return

    query = parts[0]
    text = parts[1] if len(parts) > 1 else None

    mood = (
        Mood.objects.filter(user=user, value=int(query)).first()
        if query.lstrip("-").isdigit()
        else Mood.objects.filter(user=user, name__iexact=query).first()
    )

    if not mood:
        moods = Mood.objects.filter(user=user).order_by("value")
        listing = ", ".join(f"{m.name} ({m.value})" for m in moods) or _("none")
        reply(
            gateway,
            sender_id,
            _("❌ Mood '{query}' not found.\nYour moods: {listing}").format(
                query=query, listing=listing
            ),
        )
        return

    Status.objects.create(user=user, mood=mood, text=text)
    msg = _("✅ Logged mood: {name}").format(name=mood.name)
    if text:
        msg += f"\n📝 {text}"
    reply(gateway, sender_id, msg)


@register_command("/help")
def cmd_help(user, gateway, sender_id, args):
    reply(
        gateway,
        sender_id,
        _(
            "📋 MoodyDuck Bot Commands\n\n"
            "/mood <name_or_value> [text] — Log a mood entry\n"
            "/habit <name> — Mark a habit as completed today\n"
            "/help — Show this help message\n\n"
            "Tip: send /mood or /habit without arguments to list your options."
        ),
    )
