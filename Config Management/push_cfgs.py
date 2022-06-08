#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import argparse, re
from os import listdir
from os.path import isfile, join
from github import Github
from github import InputGitTreeElement

# Class to put some color on the print output
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Get all our CLI arguments
def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--repo', required = True)
    parser.add_argument('-t', '--token', required = True)
    parser.add_argument('-p', '--path', default = './') # Defaults to user's home

    args = parser.parse_args()

    return(args)

# Inits GitHub repository
# * Token needed https://github.com/settings/tokens See section CMD Line
def init_git(repo, token):  
    g = Github(token)

    return(g.get_user().get_repo(repo))

# Gets all repository content file names
# * There will be one file name per local config file
def get_repo_content(repo):
    contents = repo.get_contents('/')
    file_list = []
    while len(contents) > 0:
        file = str(contents.pop(0).path)
        file_list.append(file)
    return(file_list)

# Gets all config files in the specified path
def get_local_content(path):
    return([file for file in listdir(path) if isfile(join(path, file)) and file.endswith('.cfg')])

# Pushes any new files existing locally but not in repo
def push_new_files(repo, local):
    try:
        new_files = list(set(get_local_content(local)) - set(get_repo_content(repo))) # Gets local files not in repo. Uses 2 sets from lists. Which words in list#1 are not in list #2
        for _ in new_files:
            file = open(_, 'r')
            repo.create_file(_, _, file.read())
    except:
        return(False)

    return(True)
# Updates existing repo files that also exist in the local path
def push_old_files(repo, local):
    try:
        old_files = list(set(get_local_content(local)) & set(get_repo_content(repo))) # Gets common files locally and repo. Uses 2 sets from lists. Which words in list#1 are also in list #2
        for _ in old_files:
            file = open(_, 'r')
            contents = repo.get_contents(_)
            repo.update_file(_, _, file.read(), contents.sha)
    except:
        return(False)
    
    return(True)

# Main function    
def main():
    args = get_arguments()
    if args.repo and args.token:
        # Init repository
        print('[' + bcolors.OKBLUE + 'I' + bcolors.ENDC + '] Init Github repository connection... ', end = '')
        repo = init_git(args.repo, args.token)
        if repo:
            print('[' + bcolors.OKGREEN + 'OK' + bcolors.ENDC + ']')
        else:
            print('[' + bcolors.FAIL + 'FAIL' + bcolors.ENDC + ']')
        # Pushes new config files
        print('[' + bcolors.OKBLUE + 'I' + bcolors.ENDC + '] Pushing new files... ', end = '')
        if push_new_files(repo, args.path):
            print('[' + bcolors.OKGREEN + 'OK' + bcolors.ENDC + ']')
        else:
            print('[' + bcolors.FAIL + 'FAIL' + bcolors.ENDC + ']')
        # Updates existing config files
        print('[' + bcolors.OKBLUE + 'I' + bcolors.ENDC + '] Updating existing files... ', end = '')
        if push_old_files(repo, args.path):
            print('[' + bcolors.OKGREEN + 'OK' + bcolors.ENDC + ']')
        else:
            print('[' + bcolors.FAIL + 'FAIL' + bcolors.ENDC + ']')

if __name__ == '__main__':
    main()
