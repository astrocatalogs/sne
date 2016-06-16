"""
"""


def main():
    from . import importer
    args = load_args()

    # Choose which submodule to run (note: can also use `set_default` with function)
    if args._name == 'importer':
        importer.importer.import_main(args)

    return


def load_args(args=None):
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate a catalog JSON file and plot HTML files from SNE data.')
    # parser.add_argument('--foo', action='store_true', help='foo help')
    subparsers = parser.add_subparsers(description='valid subcommands', dest='_name',
                                       help='sub-command help')

    # Build a 'parent' parser whose settings are inhereted by children parsers
    pars_parent = argparse.ArgumentParser(add_help=False)
    pars_parent.add_argument('--verbose', '-v', dest='verbose', default=False, action='store_true',
                             help='Print more messages to the screen.')
    pars_parent.add_argument('--travis', '-t',  dest='travis',  default=False, action='store_true',
                             help='Run import script in test mode for Travis.')

    # Construct the subparser for `importer` submodule --- importing supernova data
    pars_imp = subparsers.add_parser("importer", parents=[pars_parent],
                                     help="Generate a catalog JSON file")
    pars_imp.add_argument('--update', '-u', dest='update',
                          default=False, action='store_true',
                          help='Only update catalog using live sources.')
    pars_imp.add_argument('--refresh', '-r', dest='refresh',
                          default=False, action='store_true',
                          help='Ignore most task caches.')
    pars_imp.add_argument('--full-refresh', '-f', dest='full_refresh',
                          default=False, action='store_true',
                          help='Ignore all task caches.')
    pars_imp.add_argument('--archived', '-a', dest='archived',
                          default=False, action='store_true',
                          help='Always use task caches.')
    pars_imp.add_argument('--refreshlist', '-rl', dest='refresh_list', default='', nargs='+',
                          help='Space-delimited list of caches to clear.')

    pars_imp.add_argument('--tasks', dest='args_task_list', nargs='+', default=None,
                          help='space delimited list of tasks to perform.')
    pars_imp.add_argument('--yes', dest='yes_task_list', nargs='+', default=None,
                          help='space delimited list of tasks to perform.')
    pars_imp.add_argument('--no', dest='no_task_list', nargs='+', default=None,
                          help='space delimited list of tasks to perform.')

    args = parser.parse_args(args=args)
    if args._name is None:
        parser.print_help()

    return args
