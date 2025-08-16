import os
import subprocess
import sys
import time

from agent.models.providers.llama_cpp import call


def test_llama_cpp_provider_roundtrip():
    port = 8123
    proc = subprocess.Popen([sys.executable, "tests/dummy_llama_server.py", str(port)])
    try:
        time.sleep(0.2)  # give server time to start
        os.environ["LLAMA_CPP_BASE_URL"] = f"http://localhost:{port}"
        out = call("hi")
        assert out == "echo:hi"
    finally:
        proc.terminate()
        proc.wait()
