#!/usr/bin/env python
'''
    FILE: jenerator.py
    USAGE: python3 jenerator.py
    DESCRIPTION: Basic script, which renders Jinja2 template with the data from YAML config
    OPTIONS: See --help
    REQUIREMENTS:
      - Python >= 3.4
      - see: requirements.txt
    BUGS: Could be...
    NOTES:
    AUTHOR: Yurii Rochniak (yrochnyak@gmail.com),
    ORGANIZATION: Preply
    CREATED: 2018-12-8
    REVISION: See VERSION
'''

import os
import sys
import argparse
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader

VERSION = '0.0.1'


def create_parser():
    '''
    Parse arguments
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', default='jenerator.yaml',
                        help='Config yaml (there may be several. See docs)')
    parser.add_argument('-t', '--template', default='Jenkinsfile.jinja2',
                        help='Common template name')
    parser.add_argument('-o', '--output', default='Jenkinsfile',
                        help='Output Jenkinsfile name. In case you have set \
                        a custom name for your configuration')
    parser.add_argument('-f', '--force', action='store_true',
                        help='Force: Override a Jenkinsfile even if it exists')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose: Show YAML payload')
    parser.add_argument('--version', action='store_true', help='Show version')

    return parser


def find_conf(conf_name):
    '''
    Find config file on the filesystem
    '''

    config_list = []

    for root, _dirs, files in os.walk("./"):
        for file in files:
            if file == conf_name:
                config_list.append(os.path.join(root, file))

    return config_list

def create_pipeline(conf_name, template):
    '''
    Read the configuration from YAML
    '''

    with open(conf_name, 'r') as stream:
        try:
            config_data = yaml.load(stream)
            if ARGS.verbose:
                print("Payload from {}:\n{}".format(conf_name, config_data))
        except yaml.YAMLError as exc:
            print(exc)

    # Extended slice syntax to ensure we cut only config name
    w_dir = conf_name[::-1].replace(ARGS.config[::-1], '', 1)[::-1]
    if any(fname == template for fname in os.listdir(w_dir)):
        t_dir = w_dir
    else:
        t_dir = './templates'

    env = Environment(loader=FileSystemLoader(t_dir), trim_blocks=True, lstrip_blocks=True)

    template = env.get_template(template)
    rendered = template.render(config_data)

    return rendered

def write_pipe(fconf, render, output):
    '''
    Write rendered pipeline into the file
    '''

    # Extended slice syntax to ensure we cut only config name
    w_dir = fconf[::-1].replace(ARGS.config[::-1], '', 1)[::-1]

    o_file = w_dir + output

    if not Path(o_file).is_file() or ARGS.force:
        print("{} not found in {}. Creating...".format(output, w_dir))
        with open(o_file, 'w') as script:
            script.write(render)

    else:
        print("Jenkinsfile already exists and '--force' flag is not set. Aborting...")


if __name__ == "__main__":

    PARSE = create_parser()
    ARGS = PARSE.parse_args()

    if ARGS.version:
        print("Version: {}".format(VERSION))
        sys.exit(0)

    CONF_LIST = find_conf(ARGS.config)

    for conf in CONF_LIST:
        pipeline = create_pipeline(conf, ARGS.template)
        write_pipe(conf, pipeline, ARGS.output)
