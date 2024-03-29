from setuptools import setup, find_packages

setup(
    name='mineland',
    version='0.0.1',
    author=f'CoLa Lab',
    url='https://github.com/cocacola-lab/MineLand',
    license='MIT License',

    description='A multi-agent Minecraft simulator with large-scale interactions, limited multimodal senses and physical needs.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',

    packages=find_packages(
        where='mineland',
        include=['mineland*'],
    ),
    include_package_data=True,
    zip_safe=False,

    python_requires='>=3.11',
    install_requires=[line.strip() for line in open('requirements.txt', encoding='utf-8')],

    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
    ],
)