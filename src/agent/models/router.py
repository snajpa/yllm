"""Model router stub supporting only a local llama.cpp endpoint."""


def choose_model(step_kind: str) -> str:
    """Return the logical model name for a given step kind.

    The project currently supports a single provider backed by a
    llama.cpp server, so every step maps to that provider. The string
    "llama_cpp" is used to look up connection details in
    ``models.yaml``.
    """

    return "llama_cpp"
