#!/usr/bin/env python3

import json
import fileinput
import subprocess

log = open('123.txt', 'a')


# runs a bash command and waits for completing before proceding
def runCommand(command):
    process = subprocess.Popen(command.split(), stdout=log)
    process.wait()

# get list of platform apps to push new branches and Jenkinsfiles to
with open('/Users/Kinlaw/Documents/Development/javascript/fakamai/assets/src/platformApps.json') as f:
    data = json.load(f)

# for each platform app
for app in data['platformApps']:

    repo = app['build_repo']
    buildDir = app['path']

    # repo = 'git@github.com:RedHatInsights/cost-management-build.git'
    # buildDir = '/cost-management'

    # clone platform app into temp directory
    runCommand('git clone {} /Users/Kinlaw/tmp/repos{}'.format(repo, buildDir))

    # for each deployment environment create a stable and beta release branch and push it to the build repo
    for env in ['ci', 'qa', 'prod']:
        for release in ['stable', 'beta']:
            runCommand('git -C /Users/Kinlaw/tmp/repos{} checkout -b {}-{}'.format(buildDir, env, release))
            runCommand('git -C /Users/Kinlaw/tmp/repos{} push -u origin {}-{}'.format(buildDir, env, release))

    # for prod-beta and prod-stable, cp Jenkinsfile template and replace APP_NAME with the provided platform app path for Akamai releases
    for release in ['beta', 'stable']:
        runCommand('git -C /Users/Kinlaw/tmp/repos{} fetch --all'.format(buildDir))
        runCommand('git -C /Users/Kinlaw/tmp/repos{} checkout {}-{}'.format(buildDir, 'prod', release))
        runCommand('git -C /Users/Kinlaw/tmp/repos{} reset --hard {}-{}'.format(buildDir, 'prod', release))
        runCommand('cp /Users/Kinlaw/Documents/Development/bash/jenkinsReleases/{}-{}-Jenkinsfile /Users/Kinlaw/tmp/repos{}/Jenkinsfile'.format('prod', release, buildDir))

        with fileinput.FileInput('/Users/Kinlaw/tmp/repos{}/Jenkinsfile'.format(buildDir), inplace=True) as file:
            for line in file:
                print(line.replace('APP_NAME', buildDir), end="")

        runCommand('git -C /Users/Kinlaw/tmp/repos{} add Jenkinsfile'.format(buildDir))
        runCommand('git -C /Users/Kinlaw/tmp/repos{} commit -m "script_adding_Jenkinsfile"'.format(buildDir))
        runCommand('git -C /Users/Kinlaw/tmp/repos{} push'.format(buildDir, 'prod', release))
