class VCSCommandsBuilder:
    """ Build shell VCS command
    """
    def __init__(self, engine):
        self._engine = engine

    def tag(self, version, params):
        """
        Build and return full command to use with subprocess.Popen for 'git tag' command

        :param version:
        :param params:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'tag', '-a', '-m', 'v%s' % version, str(version)]
            if params:
                cmd.extend(params)

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def status(self):
        """
        Build and return full command to use with subprocess.Popen for 'git status' command

        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'status', '--porcelain']

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def commit(self, message):
        """
        Build and return full command to use with subprocess.Popen for 'git commit' command

        :param message:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'commit', '-m', message]

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd

    def add(self, paths):
        """
        Build and return full command to use with subprocess.Popen for 'git add' command

        :param paths:
        :return: list
        """
        cmd = None

        if self._engine == 'git':
            cmd = ['git', 'add'] + list(paths)

        if not cmd:
            raise UnknownVCSError("Unknown VCS engine: %s" % self._engine)

        return cmd


