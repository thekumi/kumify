import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from moodyduck.modules.registry import registry


class Command(BaseCommand):
    help = "Build all JS bundles (SPA + plugins) and collect static files"

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-collect",
            action="store_true",
            help="Skip collectstatic after building",
        )

    def handle(self, *args, **options):
        failed = False

        # Plugin bundles
        for slug, cfg in registry.items():
            build_dir = cfg.get("build_dir")
            if not build_dir:
                continue
            path = Path(build_dir)
            if not (path / "package.json").exists():
                self.stderr.write(
                    self.style.WARNING(f"  {slug}: no package.json in {path}, skipping")
                )
                continue
            self.stdout.write(f"Building plugin: {slug} ({path})")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=path,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.stderr.write(self.style.ERROR(f"  {slug}: build failed"))
                self.stderr.write(result.stderr)
                failed = True
            else:
                self.stdout.write(self.style.SUCCESS(f"  {slug}: ok"))

        # SPA
        spa_src = settings.BASE_DIR / "spa_src"
        if spa_src.exists():
            self.stdout.write(f"Building SPA ({spa_src})")
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=spa_src,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                self.stderr.write(self.style.ERROR("  SPA: build failed"))
                self.stderr.write(result.stderr)
                failed = True
            else:
                self.stdout.write(self.style.SUCCESS("  SPA: ok"))
        else:
            self.stderr.write(
                self.style.WARNING(f"  SPA source not found at {spa_src}")
            )

        if failed:
            self.stderr.write(
                self.style.ERROR("One or more builds failed; skipping collectstatic")
            )
            sys.exit(1)

        if not options["no_collect"]:
            self.stdout.write("Collecting static files")
            call_command("collectstatic", interactive=False, verbosity=0)
            self.stdout.write(self.style.SUCCESS("  collectstatic: ok"))
