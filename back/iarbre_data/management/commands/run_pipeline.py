import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import humanize
import yaml
from django.core.management import BaseCommand

from iarbre_data.settings import BASE_DIR

MANAGE_PY = Path(BASE_DIR) / "manage.py"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _humanize(seconds: float) -> str:
    return humanize.precisedelta(
        timedelta(seconds=int(seconds)), minimum_unit="seconds"
    )


def _pipeline_slug(name: str) -> str:
    table = str.maketrans("éèêëàâùûôîïç ", "eeeea auuoiic_")
    return name.lower().translate(table)


def _load_state(state_path: Path) -> dict:
    if state_path.exists():
        return json.loads(state_path.read_text(encoding="utf-8"))
    return {}


def _save_state(state: dict, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _build_command(node: dict) -> list[str]:
    cmd = [sys.executable, str(MANAGE_PY), node["command"]]
    for key, value in node.get("args", {}).items():
        if isinstance(value, bool):
            if value:
                cmd.append(f"--{key}")
        else:
            cmd.extend([f"--{key}", str(value)])
    return cmd


def _run_node(node: dict) -> tuple[int, float]:
    cmd = _build_command(node)
    start = time.monotonic()
    result = subprocess.run(cmd, cwd=str(MANAGE_PY.parent))
    return result.returncode, time.monotonic() - start


class Command(BaseCommand):
    help = "Run the plantability data pipeline defined in a YAML config file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--config",
            default="pipeline/plantability_pipeline.yaml",
            help="Path to the pipeline YAML config (relative to project root)",
        )
        parser.add_argument(
            "--state",
            default=None,
            help="Path to the JSON state file. Defaults to output/pipeline_<name>_state.json",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would run without executing anything",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Clear the existing state and restart the pipeline from scratch",
        )

    def handle(self, *args, **options):
        config_path = Path(BASE_DIR) / options["config"]
        if not config_path.exists():
            self.stderr.write(self.style.ERROR(f"Config not found: {config_path}"))
            return

        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        pipeline_name = config["name"]
        nodes = config["nodes"]

        if options["state"]:
            state_path = Path(options["state"])
        else:
            slug = _pipeline_slug(pipeline_name)
            state_path = Path(BASE_DIR) / "output" / f"pipeline_{slug}_state.json"

        state = {} if options["reset"] else _load_state(state_path)

        if options["dry_run"]:
            self._print_dry_run(
                pipeline_name, config.get("description", ""), nodes, state
            )
            return

        if not state.get("pipeline_started_at"):
            state["pipeline_started_at"] = _now_iso()

        state.update(
            pipeline=pipeline_name,
            config_file=str(config_path),
            state_file=str(state_path),
            pipeline_status="running",
            pipeline_completed_at=None,
            pipeline_duration=None,
            pipeline_duration_seconds=None,
        )
        state.setdefault("nodes", {})
        _save_state(state, state_path)

        self.stdout.write(f"\nPipeline : {pipeline_name}")
        self.stdout.write(f"State    : {state_path}\n")

        run_start = time.monotonic()
        succeeded = True

        for node in nodes:
            node_id = node["id"]
            node_state = state["nodes"].get(node_id, {})

            if node_state.get("status") == "completed":
                self.stdout.write(f"  [skip]  {node['name']}")
                continue

            deps = node.get("depends_on", [])
            unmet = [
                d
                for d in deps
                if state["nodes"].get(d, {}).get("status") != "completed"
            ]
            if unmet:
                self.stderr.write(
                    self.style.ERROR(
                        f"  [blocked] {node['name']} — unmet dependencies: {unmet}"
                    )
                )
                succeeded = False
                break

            self.stdout.write(f"\n→ {node['name']}")
            node_state.update(
                name=node["name"], status="running", started_at=_now_iso()
            )
            state["nodes"][node_id] = node_state
            _save_state(state, state_path)

            return_code, duration = _run_node(node)

            node_state["completed_at"] = _now_iso()
            node_state["duration_seconds"] = round(duration, 2)
            node_state["duration"] = _humanize(duration)

            if return_code == 0:
                node_state["status"] = "completed"
                node_state.pop("return_code", None)
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ completed in {node_state['duration']}")
                )
            else:
                node_state["status"] = "failed"
                node_state["return_code"] = return_code
                self.stderr.write(
                    self.style.ERROR(
                        f"  ✗ failed (exit {return_code}) after {node_state['duration']}"
                    )
                )
                succeeded = False

            state["nodes"][node_id] = node_state
            _save_state(state, state_path)

            if not succeeded:
                break

        total = time.monotonic() - run_start
        state["pipeline_completed_at"] = _now_iso()
        state["pipeline_duration_seconds"] = round(total, 2)
        state["pipeline_duration"] = _humanize(total)
        state["pipeline_status"] = "completed" if succeeded else "failed"
        _save_state(state, state_path)

        self.stdout.write(f"\nState saved to: {state_path}")
        if succeeded:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Pipeline completed in {state['pipeline_duration']}"
                )
            )
        else:
            self.stderr.write(
                self.style.ERROR(
                    f"Pipeline failed after {state['pipeline_duration']}. "
                    "Re-run the same command to resume from the last failed step."
                )
            )

    def _print_dry_run(
        self, name: str, description: str, nodes: list, state: dict
    ) -> None:
        self.stdout.write(f"\nPipeline: {name}")
        if description:
            self.stdout.write(description.strip())
        self.stdout.write("\nExecution order:")
        for node in nodes:
            node_id = node["id"]
            status = state.get("nodes", {}).get(node_id, {}).get("status", "pending")
            deps = ", ".join(node.get("depends_on", [])) or "—"
            cmd = " ".join(_build_command(node)[2:])
            self.stdout.write(
                f"  [{status:^10}]  {node['name']}\n"
                f"               command: {cmd}\n"
                f"               depends_on: {deps}"
            )
