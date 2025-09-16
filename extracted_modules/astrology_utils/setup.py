from setuptools import setup, find_packages

setup(
    name="astrology-utils",
    version="1.0.0",
    author="TwitterBot Project",
    description="占星術計算・解釈・恋愛占いの統合ユーティリティライブラリ",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "swisseph>=2.8.0",
        "pyephem>=4.1.0",
        "pytz>=2021.1",
        "requests>=2.25.0",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="astrology horoscope zodiac fortune ai gemini swisseph",
    project_urls={
        "Source": "https://github.com/your-username/astrology-utils",
        "Bug Reports": "https://github.com/your-username/astrology-utils/issues",
    },
)