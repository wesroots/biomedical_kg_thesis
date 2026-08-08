import importlib
from datetime import datetime

def rel(*args):
    for module in args:
        importlib.reload(module)
        print(
            f"Reloaded '{module.__name__}' module at "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}."
        )


def print_epi_summary(
    epi_num,
    prompt_version,
    eval_version,
    notes,
    reuse_api_call
):
    print(f"Cell ran at {datetime.now():%Y-%m-%d %H:%M} for epi_{epi_num}")
    print(f" - Prompt version: {prompt_version}")
    print(f" - Evaluation version: {eval_version}")
    print(f" - Notes: {notes}")
    print(f" - Reuse API Call: {reuse_api_call}")