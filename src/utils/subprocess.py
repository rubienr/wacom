import subprocess
from typing import List


def run_subprocess(args, verbose: bool = False, **kwargs) -> subprocess.CompletedProcess:
    stdout = kwargs.pop("stdout", subprocess.PIPE)
    stderr = kwargs.pop("stderr", subprocess.PIPE)
    shell = kwargs.pop("shell", True)
    text = kwargs.pop("text", True)
    check = kwargs.pop("check", False)

    if verbose:
        print(f"$ {args}")
    return subprocess.run(args, stdout=stdout, stderr=stderr, shell=shell, text=text, check=check, **kwargs)


def lines_from_stream(lines_stream) -> List[str]:
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []
