from setuptools import setup, find_packages

setup(
    name="chrome-automation-utils",
    version="1.0.0",
    author="TwitterBot Project",
    description="Chrome自動化とプロファイル管理のための統合ユーティリティライブラリ",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "selenium>=4.0.0",
        "webdriver-manager>=3.8.0",
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
    keywords="selenium chrome profile webdriver automation browser-automation stealth",
    project_urls={
        "Source": "https://github.com/your-username/chrome-automation-utils",
        "Bug Reports": "https://github.com/your-username/chrome-automation-utils/issues",
    },
)