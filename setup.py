from distutils.core import setup

setup(
    name='homekit',
    packages=['homekit', 'homekit.model'],  # this must be the same as the name above
    version='0.3',
    description='Python code to interface HomeKit Accessories and Controllers',
    author='Joachim Lusiardi',
    author_email='pypi@lusiardi.de',
    url='https://github.com/jlusiardi/homekit_python',  # use the URL to the github repo
    download_url='https://github.com/jlusiardi/homekit_python/archive/0.2.tar.gz',  # I'll explain this in a second
    keywords=['HomeKit'],  # arbitrary keywords
    classifiers=[],
    install_requires=[
        'zeroconf',
        'gmpy2',
        'py25519',
        'hkdf',
        'ed25519',
        'netifaces',
    ],
)
