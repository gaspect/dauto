import nox

@nox.session(python=False)
def docs(session):
    session.run('pylliterate', 'build')
    session.run('mkdocs', 'build')
    session.run('mkdocs', 'gh-deploy')