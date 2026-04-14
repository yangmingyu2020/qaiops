"""QaiOps CLI — Universal AI CLI Wrapper.

Usage:
    qaiops run <tool> "<prompt>"
    qaiops server          # Start the log server
"""

import subprocess
import sys
import time

import click

from qaiops.wrapper.metadata import get_cwd, get_project_id, get_timestamp
from qaiops.wrapper.parsers import get_parser
from qaiops.wrapper.sender import send_log_async

# 도구명 → 실제 CLI 명령 매핑
TOOL_COMMANDS: dict[str, str] = {
    "claude": "claude",
    "gemini": "gemini",
    "gpt": "codex",
    "codex": "codex",
}


@click.group()
def cli():
    """QaiOps - AI CLI Observability for Developers."""
    pass


@cli.command()
@click.argument("tool_name")
@click.argument("prompt")
def run(tool_name: str, prompt: str):
    """Run an AI CLI tool and log the interaction.

    TOOL_NAME: Name of the AI tool (claude, gemini, gpt)
    PROMPT: The prompt to send to the tool
    """
    # 메타데이터 수집
    project_id = get_project_id()
    directory = get_cwd()
    timestamp = get_timestamp()

    # 도구 명령어 매핑
    tool_cmd = TOOL_COMMANDS.get(tool_name, tool_name)

    # 실행
    start_time = time.time()
    try:
        result = subprocess.run(
            [tool_cmd, prompt],
            capture_output=True,
            text=True,
            timeout=300,  # 5분 타임아웃
        )
        latency_ms = int((time.time() - start_time) * 1000)
        status_code = 0 if result.returncode == 0 else 1
        error_message = result.stderr.strip() if result.returncode != 0 else None

    except subprocess.TimeoutExpired:
        latency_ms = int((time.time() - start_time) * 1000)
        click.echo(f"[qaiops] Error: {tool_name} timed out after 300 seconds", err=True)
        # 타임아웃도 로그 전송
        payload = {
            "tool_name": tool_name,
            "project_id": project_id,
            "directory": directory,
            "prompt_text": prompt,
            "latency_ms": latency_ms,
            "status_code": 2,
            "error_message": "Timeout after 300 seconds",
        }
        send_log_async(payload)
        sys.exit(124)

    except FileNotFoundError:
        click.echo(
            f"[qaiops] Error: '{tool_cmd}' command not found. "
            f"Please install {tool_name} CLI first.",
            err=True,
        )
        sys.exit(127)

    # 사용자에게 도구 출력 표시 (투명한 래핑)
    if result.stdout:
        click.echo(result.stdout, nl=False)
    if result.stderr and result.returncode != 0:
        click.echo(result.stderr, err=True, nl=False)

    # 파서로 출력 분석
    parser = get_parser(tool_name)
    parsed = parser(result.stdout, result.stderr)

    # 로그 페이로드 구성
    payload = {
        "tool_name": tool_name,
        "model_name": parsed.model_name,
        "project_id": project_id,
        "directory": directory,
        "prompt_text": prompt,
        "response_text": parsed.response_text,
        "input_tokens": parsed.input_tokens,
        "output_tokens": parsed.output_tokens,
        "latency_ms": latency_ms,
        "status_code": status_code,
        "error_message": error_message,
        "raw_response": parsed.raw_response,
    }

    # 비동기 로그 전송 (fire-and-forget)
    send_log_async(payload)

    # 도구의 exit code로 종료
    sys.exit(result.returncode)


@cli.command()
@click.option("--port", default=8765, help="Server port (default: 8765)")
@click.option("--host", default="127.0.0.1", help="Server host (default: 127.0.0.1)")
def server(port: int, host: str):
    """Start the QaiOps log server."""
    import uvicorn

    click.echo(f"Starting QaiOps server at http://{host}:{port}")
    click.echo("API docs: http://{host}:{port}/docs")
    uvicorn.run("qaiops.server.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    cli()
