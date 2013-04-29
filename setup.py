from distutils.core import setup

setup(  name='apiblender',
        version='0.4',
        description='API Blender allows you to easily interact with many APIs',
        author='Georges Gouriten',
        author_email='georges.gouriten@gmail.com',
        url='http://github.com/netiru/apiblender',
        packages=['apiblender'],
        package_data={'apiblender': [   'config/*.json', 
                                        'config/apis/*.json',
                                        'config/apis/auth/*.example']},
        requires = ['oauth2', 'xmltodict'],
        license = "GNU/GPL v3 License",
        keywords="api"    )

