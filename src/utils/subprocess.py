import subprocess
from typing import List


def run_subprocess(args, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(args,
                          stdout=kwargs.pop("stdout", subprocess.PIPE),
                          stderr=kwargs.pop("stderr", subprocess.PIPE),
                          shell=kwargs.pop("shell", True),
                          text=kwargs.pop("text", True),
                          **kwargs)


def lines_from_stream(lines_stream) -> List[str]:
    return str(lines_stream.strip()).split('\n') if len(lines_stream) > 0 else []
