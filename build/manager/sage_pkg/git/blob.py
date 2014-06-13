"""
Git Blobs
"""


import os
import re
import zlib

from sage_pkg.logger import logger


BLOB_RE = re.compile(r'(?P<type>[a-z]*) (?P<size>[0-9]*)\0(?P<content>.*)', flags=re.DOTALL)

BLOB_COMMIT_TREE_RE = re.compile(r'tree (?P<sha1>[a-f0-9]{40,40})')


def Blob(filename):
    """
    Load the git object with given sha1 hash
    """
    with open(filename, 'rb') as f:
        blob = zlib.decompress(f.read())
    match = BLOB_RE.match(blob)
    if not match:
        raise ValueError('file is not a git object')
    if blob.startswith('commit'):
        return BlobCommit(match)
    if blob.startswith('tree'):
        return BlobTree(match)
    if blob.startswith('blob'):
        return BlobFile(match)
    raise ValueError('unsupported blob: ' + repr(blob))


class BlobABC(object):
    
    def __init__(self, match):
        self._type = match.group('type')
        self._size = int(match.group('size'))
        self._content = match.group('content')

    def __repr__(self):
        s = [self.__class__.__name__ + ':']
        for line in self._content.splitlines():
            if len(line.strip()) == 0:
                continue
            s.append('    ' + line.rstrip())
        return '\n'.join(s)


class BlobCommit(BlobABC):
    
    @property
    def tree(self):
        """
        Return the tree sha1 that is being committed
        
        EXAMPLES::

            >>> commit = git.get_symbolic_ref('HEAD')
            >>> type(commit)
            <class 'sage_pkg.git.blob.BlobCommit'>
            >>> commit.tree    # doctest: +SKIP
            'f1795efaddd86273a715baf26a80c908a132a035'
            >>> len(commit.tree) == 40 and int(commit.tree, 16) >= 0
            True
        """
        match = BLOB_COMMIT_TREE_RE.match(self._content)
        return match.group('sha1')

    
class BlobTree(BlobABC):

    MODE_NORMAL = '100644'
    MODE_EXEC = '100755'
    MODE_DIR = '40000'

    def ls(self):
        """
        Iterate over the tree content
        
        EXAMPLES::

            >>> commit = git.get_symbolic_ref('HEAD')
            >>> tree = git.get(commit.tree)
            >>> type(tree)
            <class 'sage_pkg.git.blob.BlobTree'>
            >>> for item in tree.ls():   # doctest: +ELLIPSIS
            ...     print(item)
            ('100644', '.gitignore', ...
        """
        pos = 0
        while pos < len(self._content):
            pos_space = self._content.find(' ', pos + 1)
            mode = self._content[pos:pos_space]
            pos_zero = self._content.find('\0', pos_space + 1)
            name = self._content[pos_space + 1:pos_zero]
            sha1_binary = self._content[pos_zero + 1:pos_zero + 21]
            sha1 = ''.join('{0:02x}'.format(ord(c)) for c in sha1_binary)
            yield (mode, name, sha1)
            pos = pos_zero + 21

    def __repr__(self):
        """
        Iterate over the tree content
        
        Override the generic repr since the tree object contains binary sha1's.

        EXAMPLES::

            >>> commit = git.get_symbolic_ref('HEAD')
            >>> git.get(commit.tree)   # doctest: +ELLIPSIS
            BlobTree:
                100644 ...
        """
        s = [self.__class__.__name__ + ':']
        for mode, name, sha1 in self.ls():
            s.append('    {0:>6} {1} {2}'.format(mode, sha1, name))
        return '\n'.join(s)

    def ls_dirs(self):
        """
        Iterater over the sub-trees
        
        EXAMPLES::

            >>> commit = git.get_symbolic_ref('HEAD')
            >>> tree = git.get(commit.tree)
            >>> type(tree)
            <class 'sage_pkg.git.blob.BlobTree'>
            >>> for item in tree.ls_dirs():   # doctest: +ELLIPSIS
            ...     print(item)
            ('40000', 'build', ...
        """
        for dirent in self.ls():
            if dirent[0] == self.MODE_DIR:
                yield dirent

    def get(self, filename):
        """
        Return the sha1 of a file in the tree

        EXAMPLES::

            >>> commit = git.get_symbolic_ref('HEAD')
            >>> tree = git.get(commit.tree)
            >>> sha1 = tree.get('.gitignore')
            >>> sha1  # doctests: +SKIP
            'a9b6be08742e31b728f04f6f89c4b93f28ac4b92'
            >>> len(sha1) == 40 and int(sha1, 16) >= 0
            True
        """
        for mode, name, sha1 in self.ls():
            if name == filename:
                return sha1
        raise ValueError('file is not in the tree')

    def _compare_files(self, dirname, verbose=False):
        """
        Helper to just compare the files
        """


class BlobFile(BlobABC):
    pass
    

