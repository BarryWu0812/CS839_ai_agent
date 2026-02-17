import argparse
import json
import os
import sys
from pathlib import Path

from litellm import completion

from cli_agent.tools import TOOLS, execute_tool


DEFAULT_SYSTEM = (
    "You are a CLI coding agent. Keep responses concise and actionable. "
    "When useful, call tools to inspect or modify files."
)


def _message_to_dict(message) -> dict:
    if hasattr(message, "model_dump"):
        return message.model_dump()
    if isinstance(message, dict):
        return message
    return {"role": "assistant", "content": str(message)}


def _print_tool_call(name: str, args: dict) -> None:
    print(f"[tool] {name}({json.dumps(args, ensure_ascii=True)})")


def _print_tool_result(result: str) -> None:
    print(f"[tool result] {result}")


def run_agent(model: str, max_steps: int, verbose: bool, system_prompt: str) -> None:
    workspace_root = Path.cwd()
    messages = [{"role": "system", "content": system_prompt}]

    print("CLI Coding Agent. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("agent> ").strip()
        except EOFError:
            print()
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            break

        messages.append({"role": "user", "content": user_input})

        for _ in range(max_steps):
            response = completion(model=model, messages=messages, tools=TOOLS)
            assistant_msg = response.choices[0].message
            messages.append(_message_to_dict(assistant_msg))

            tool_calls = getattr(assistant_msg, "tool_calls", None)
            if not tool_calls:
                content = assistant_msg.content or ""
                print(content.strip())
                break

            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments or "{}")
                if verbose:
                    _print_tool_call(tool_name, args)
                result = execute_tool(tool_name, args, workspace_root)
                if verbose:
                    _print_tool_result(result)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )
        else:
            print("Max tool steps reached; aborting.")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI coding agent")
    parser.add_argument(
        "--model",
        default=os.environ.get("AGENT_MODEL", "openai/gpt-4o-mini"),
        help="Model name (e.g., openai/gpt-4o-mini, anthropic/claude-3-5-sonnet).",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=8,
        help="Maximum tool steps per user turn.",
    )
    parser.add_argument(
        "--system",
        default=DEFAULT_SYSTEM,
        help="Override the system prompt.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print tool calls and results.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if not args.model:
        print("Model is required. Set --model or AGENT_MODEL.")
        return 2

    run_agent(
        model=args.model,
        max_steps=args.max_steps,
        verbose=args.verbose,
        system_prompt=args.system,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
