from setuptools import setup

setup(
    name="scratch",
    version="0.1",
    description=("dirtily written utils in python"),
    author="Sarfaraz Ahmad",
    author_email="sarfaraz19@live.com",
    license="MIT",
    packages=["scratch"],
    install_requires=[
        "httpx==0.24.1",
        "typer==0.9.0",
        "typing_extensions==4.6.3",
        "rich",
    ],
    zip_safe=False,
    entry_points="""
        [console_scripts]
        pydownloader=scratch.pydownloader:launch
      """,
)
