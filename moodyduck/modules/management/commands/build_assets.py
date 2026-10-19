import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
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
        parser.add_argument(
            "--force",
            action="store_true",
            help="Rebuild plugin bundles even if already present",
        )

    def handle(self, *args, **options):
        failed = False
        force = options["force"]

        # Plugin bundles
        for slug, cfg in registry.items():
            build_dir = cfg.get("build_dir")
            if not build_dir:
                continue
            path = Path(build_dir)

            if not force:
                bundle_url = cfg.get("bundle_url", "")
                if bundle_url:
                    static_rel = bundle_url.removeprefix(settings.STATIC_URL)
                    if finders.find(static_rel):
                        self.stdout.write(f"  {slug}: pre-built bundle found, skipping")
                        continue

            if not (path / "package.json").exists():
                self.stderr.write(
                    self.style.WARNING(
                        f"  {slug}: bundle missing from installed package"
                        f" and no build source found at {path}"
                    )
                )
                continue

            self.stdout.write(f"Building plugin: {slug} ({path})")

            if not (path / "node_modules").exists():
                self.stdout.write(f"  {slug}: running npm ci")
                result = subprocess.run(
                    ["npm", "ci"],
                    cwd=path,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    self.stderr.write(self.style.ERROR(f"  {slug}: npm ci failed"))
                    self.stderr.write(result.stderr)
                    failed = True
                    continue

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
            spa_out = settings.BASE_DIR / "spa"
            if not force and (spa_out / "index.html").exists():
                self.stdout.write("  SPA: pre-built output found, skipping")
            else:
                self.stdout.write(f"Building SPA ({spa_src})")
                if not (spa_src / "node_modules").exists():
                    self.stdout.write("  SPA: running npm ci")
                    result = subprocess.run(
                        ["npm", "ci"],
                        cwd=spa_src,
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode != 0:
                        self.stderr.write(self.style.ERROR("  SPA: npm ci failed"))
                        self.stderr.write(result.stderr)
                        failed = True
                if not failed:
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
