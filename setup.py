import setuptools

setuptools.setup(
    version="0.0.1",
    license='mit',
    name="slackbot",
    author='nathan todd-stone',
    author_email='me@nathants.com',
    url='http://github.com/nathants/slackbot',
    description='slackbot',
    install_requires=['requests',
                      'boto3'],
    py_modules=['slackbot']
)
