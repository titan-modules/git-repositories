#!/usr/bin/env python
"""
This is a Titan module

- Analyze Git Repositories is to let the administrators
  know what data is checked out on a device in the event
  of a compromise or the misplacement of a device

To use:

    sudo pip install --upgrade titantools

"""

import json
import logging
from sys import argv
from titantools.orm import TiORM
from titantools.data_science import DataScience
from titantools.system import execute_command

# from sys import argv
from time import time, gmtime, strftime
from os.path import dirname,basename,isfile
from os import chmod
from titantools.decorators import run_every_60

# Set Logging Status
logging_enabled = False

# Set datastore directory
DATASTORE = argv[1]

@run_every_60
class AnalyzeGitCheckouts(object):
    """ AnalyzeGitCheckouts """

    def __init__(self):
      self.message = type(self).__name__
      self.status = 0
      self.datastore = []

    def check_git_dirs(self):
      """
      Log all loaded kernel extensions
      """
      repos = execute_command('find /Users -type d -name ".git"').splitlines()

      for repo in repos:

        repo_path = dirname(repo)
        repo_git_path = repo
        repo_name = basename(dirname(repo))

        if logging_enabled:
          print "Found '%s' @ '%s'" % (repo_name, repo_path)           

        # Get latest commit
        most_recent_commit = execute_command('git --git-dir="%s" --work-tree="%s"  log --pretty=format:"%%cd|[Commit: %%h] [Date: %%cd] [Commiter: %%cn] [Commiter Email: %%ce] [Message: %%s]" -1' % (repo_git_path, repo_path)).split("|", 1)

        commit_date = most_recent_commit[0]
        commit_details = most_recent_commit[1] 
         
        # Get remote
        remotes = execute_command("git --git-dir=%s --work-tree=%s remote -v" % (repo_git_path, repo_path))

        # Append to master
        self.datastore.append({
            "name": repo_name,
            "path": repo_path,
            "commit_date": commit_date,
            "last_commit": commit_details,
            "remotes": remotes,
            "date": exec_date
          })

      # Set Message
      self.message = "Found %d repositories" % len(self.datastore)

      # If no issues, return 0
      self.status = 0

    def analyze(self):
      """
      This is the 'main' method that launches all of the other checks
      """
      self.check_git_dirs()

      return json.JSONEncoder().encode({"status": self.status, "message": self.message})

    def store(self):
      # the table definitions are stored in a library file. this is instantiating
      # the ORM object and initializing the tables
      module_schema_file = '%s/schema.json' % dirname(__file__)

      # Is file
      if isfile(module_schema_file):
        with open(module_schema_file) as schema_file:   
          schema = json.load(schema_file)

        # ORM 
        ORM = TiORM(DATASTORE)
        if isfile(DATASTORE):
            chmod(DATASTORE, 0600)
        for k, v in schema.iteritems():
            ORM.initialize_table(k, v)

        data_science = DataScience(ORM, self.datastore, "git_repos")
        data_science.get_all()

if __name__ == "__main__":

    start = time()

    # the "exec_date" is used as the "date" field in the datastore
    exec_date = strftime("%a, %d %b %Y %H:%M:%S", gmtime())

    ###########################################################################
    # Gather data
    ###########################################################################
    try:
        a = AnalyzeGitCheckouts()
        if a is not None:
            output = a.analyze()
            a.store()
            print output

    except Exception, error:
        print error

    end = time()

    # to see how long this module took to execute, launch the module with
    # "--log" as a command line argument
    if "--log" in argv[1:]:
      logging_enabled = True
      logging.basicConfig(format='%(message)s', level=logging.INFO)
    
    logging.info("Execution took %s seconds.", str(end - start))
