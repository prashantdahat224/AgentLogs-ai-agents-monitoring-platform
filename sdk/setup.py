from setuptools import setup, find_packages

setup(
    name="agentlogs",
    version="1.0.0",
    description="AI agent observability — 2 lines of code to monitor your agents",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.8",
)