import codecs, os, tempfile, subprocess

class GitBackend(object):
    def __init__(self, repo_url):
        self.repo_url = repo_url

    def write(path, content, msg=None, user=None):
        checkout_dir = tempfile.mkdtemp()
        with cd(checkout_dir):
            subprocess.call(['git', 'clone', 
                             self.repo_url, '.'])
            filename = os.path.join(checkout_dir, self.filename)
            dir = os.path.dirname(filename)
            try:
                os.makedirs(dir)
            except:
                pass
            fp = codecs.open(filename, 'w', encoding='utf8')
            fp.write(self.code)
            fp.close()
            subprocess.call(['git', 'add', self.filename])
            if user is not None and user.get_full_name() and user.email:
                subprocess.call(['git', 'commit', '--author', '%s <%s>' % (user.get_full_name(), user.email), '-m', msg])
            else:
                subprocess.call(['git', 'commit', '-m', msg])
            subprocess.call(['git', 'push'])
        
