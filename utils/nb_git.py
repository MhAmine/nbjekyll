import pygit2
import os

import fnmatch
import glob
from pathlib import Path
from datetime import datetime
import pytz

class nb_repo(object):
    """ Class containing methods used to
    identify the notebooks committed to the
    repository and add the SHA to the Jinja template"""

    def __init__(self, here):
        """ Find if the current location is a
        Git repository, if so it will return a
        repository object """
        try:
            repo_path = pygit2.discover_repository(here)
            repo = pygit2.Repository(repo_path)
            self.repo = repo
            self.here = here
        except:
            raise IOError ('This does not seem to be a repository')


    def check_log(self):
        """ Check the number of commits in the repository,
        if there is only one commit it will find all the notebooks
        inside the repository.
        Otherwise, it will find the notebooks in the latest commit only
        Returns
            -------
            notebooks: dictionary containing the sha1 for the commit,
            the list of found notebooks, author, and the date when
            the notebooks were last updated
        """
        all_commits = [commit for commit in self.repo.head.log()]
        if len(all_commits) <= 1:
            print('Only one commit: converting all notebooks')
            # calls function find_notebooks
            notebooks = self.find_notebooks()
            commit_info = self.get_commit()
            commit_info['notebooks'] = notebooks

            return commit_info
        else:
            print(("There are notebooks already in version control,"
                   "finding the notebooks passed in the last commit"))
            # calls function last_commit
            notebooks = self.last_commit()
            return notebooks

    def find_notebooks(self):
        """ Find all the notebooks in the repo, but excludes those
        in the _site folder.
        Returns
            -------
            notebooks: dictionary containing the sha1, notebooks name,
            and dat of the commit
        """
        basePath = Path(os.getcwd())
        notebooksAll = [nb for nb in glob.glob('**/*.ipynb')]
        exception = os.path.join(basePath, '/_site/*/*')
        notebooks = [nb for nb in notebooksAll if not fnmatch.fnmatch(nb, exception)]

        if not(notebooks) == True:
            print('There were no notebooks found')
        else:
            return notebooks

    def last_commit(self):
        """ Find the notebooks modified in the last repository, but excludes those
                in the _site folder.
                Returns
                    -------
                    notebooks: dictionary containing the sha1, notebooks name,
                    and dat of the commit
                    if no notebooks were modified in the last commit then
                    the list notebooks is an empty list
        """

        commit_info = self.get_commit()
        notebooks = [nb.name for nb in self.repo.revparse_single('HEAD').tree if '.ipynb' in nb.name]
        commit_info['notebooks'] = notebooks

        return commit_info

    def convert_time(self, epoch):
        """
        Pass on the epoch date from the last commit and
        returns it in a human readable format
        :param epoch:
        :return: commit date in a dd-mm-YYYY format
        """
        time_zone = pytz.timezone('GMT')
        dt = datetime.fromtimestamp(epoch, time_zone)

        return dt.strftime('%d-%m-%Y')

    def get_commit(self):
        """
        Get the information for the last commit in the repository
        :return: dictionary with the sha1, date, and author
        of the last commit.
        """
        last = self.repo.revparse_single('HEAD')
        sha1 = last.hex[0:7]
        author = last.author.name
        date = self.convert_time(last.author.time)
        commit_info = {'sha1': sha1,
                   'date': date,
                   'author': author}

        return commit_info
