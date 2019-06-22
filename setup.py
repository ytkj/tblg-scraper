import setuptools

install_requires = [
    'selenium',
    'chromedriver_binary',
    'pandas',
]

setuptools.setup(
    name='tblg_scraper',
    install_requires=install_requires,
    packages=setuptools.find_packages(),
)