from invoke import run, task

from os.path import join, abspath, dirname

ROOT = abspath(join(dirname(__file__)))


def compose(ctx, cmd):
    '''Run a docker-compose command'''
    return ctx.run('docker-compose {0}'.format(cmd), pty=True)


@task
def clean(ctx, docs=False, bytecode=False, extra=''):
    '''Cleanup all build artifacts'''
    patterns = ['build', 'dist', 'cover', 'docs/_build', '**/*.pyc', '*.egg-info', '.tox']
    for pattern in patterns:
        print('Removing {0}'.format(pattern))
        with ctx.cd(ROOT):
            ctx.run('rm -rf {0}'.format(pattern))


@task
def start(ctx):
    '''Start the middlewares (docker)'''
    with ctx.cd(ROOT):
        compose(ctx, 'up -d')
        compose(ctx, 'ps')


@task
def stop(ctx, rm=False):
    '''Stop the middlewares (docker)'''
    with ctx.cd(ROOT):
        compose(ctx, 'stop')
        if rm:
            compose(ctx, 'rm --force')


@task
def test(ctx):
    '''Run tests suite'''
    with ctx.cd(ROOT):
        ctx.run('pytest', pty=True)


@task
def cover(ctx, html=False):
    '''Run tests suite with coverage'''
    params = '--cov-report term --cov-report html' if html else ''
    with ctx.cd(ROOT):
        ctx.run('pytest --cov flask_fs {0}'.format(params), pty=True)


@task
def tox(ctx):
    '''Run tests against Python versions'''
    run('tox', pty=True)


@task
def qa(ctx):
    '''Run a quality report'''
    with ctx.cd(ROOT):
        ctx.run('flake8 flask_fs tests')


@task
def doc(ctx):
    '''Build the documentation'''
    with ctx.cd(ROOT):
        ctx.run('cd docs && make html', pty=True)


@task
def dist(ctx):
    '''Package for distribution'''
    with ctx.cd(ROOT):
        ctx.run('python setup.py sdist bdist_wheel', pty=True)


@task(start, tox, doc, qa, dist, default=True)
def all(ctx):
    '''Run tests, reports and packaging'''
    pass
