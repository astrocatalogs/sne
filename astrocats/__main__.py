"""
"""

import importlib
import os
import sys
from datetime import datetime

from astrocats import __version__, __git_version__, argshandler
from astrocats.utils import logger, gitter

_PROFILE = False


def main():
    """Primary entry point for all AstroCats catalogs.

    From this entry point, all internal catalogs can be accessed and their
    public methods executed (for example: import scripts).

    """

    # Initialize: Load command line arguments, log, etc
    # ----------------------------------------------------
    args = argshandler.parse_args()
    if args is None:
        return

    # Create a logging object
    log = load_log(args)

    title_str = "Astrocats, version: {}, SHA: {}".format(__version__, __git_version__)
    log.warning("\n{}\n{}\n".format(title_str, '=' * len(title_str)))

    beg_time = datetime.now()
    log.info("{}\n".format(beg_time.ctime()))

    log.info("command: '{}'".format(args.command))
    log.info("catalog: '{}'".format(args.catalog))

    # Load target catalog module
    # ----------------------------------------

    catalog_path = args.catalog
    catalog_path = os.path.realpath(os.path.abspath(catalog_path))
    log.debug("Importing specified catalog module: '{}'".format(catalog_path))

    if not os.path.exists(catalog_path):
        log.raise_error("`catalog_path` '{}' does not exist!".format(catalog_path))

    if not os.path.isdir(catalog_path):
        log.raise_error("`catalog_path` '{}' is not a directory!".format(catalog_path))

    # Try to import the specified module
    try:
        # catalog_module = importlib.import_module('.' + mod_name, package='astrocats')
        # Get the location of the module to add to `sys.path`
        catalog_path_dir = os.path.dirname(catalog_path)
        catalog_module_name = os.path.basename(catalog_path)

        # Insert the path to this module.  Make it first to avoid builtin package conflicts
        log.debug("adding catalog module path: '{}'".format(catalog_path_dir))
        sys.path.insert(0, catalog_path_dir)

        # Import catalog module
        log.debug("importing catalog module name: '{}'".format(catalog_module_name))
        catalog_module = importlib.import_module(catalog_module_name)

        # Remove added path to avoid unintended imports
        sys.path.pop(0)
        log.info("Loaded: '{}'".format(str(catalog_module)))

    except Exception as err:
        msg = "Import of specified catalog module '{}' failed.".format(catalog_path)
        log.raise_error(msg, err)

    # Perform setup operations before loading the target catalog
    # -----------------------------------------------------------
    setup(log)

    # Construct a catalog instance based on the loaded module
    try:
        catalog_package_name = catalog_module.__name__
        catalog_class_name = catalog_module.catalog_class['name']
        catalog_class_file = catalog_module.catalog_class['file']
        catalog_class_path = catalog_module.catalog_class['import_path']
        log.info("{} {} {}".format(catalog_package_name, catalog_class_name, catalog_class_path))
        # catalog = catalog_module.Catalog_Class(args, log)
        mod = catalog_class_file
        mod_path = catalog_class_path
        # print(mod_path, mod)
        catalog_file = importlib.import_module(mod_path + mod)  # , package=mod_path)
        Catalog_Class = getattr(catalog_file, catalog_class_name)
        catalog = Catalog_Class(args, log)

    except Exception as err:
        raise

    # Perform setup operations with the target catalog
    setup_catalog(catalog)

    # Run target command in the given catalog module
    # -----------------------------------------------------------

    if _PROFILE:
        msg = "RUNNING IN PROFILE MODE"
        log.warning("")
        log.warning("="*len(msg))
        log.warning(msg)
        log.warning("="*len(msg))
        log.warning("")
        import cProfile
        pr = cProfile.Profile()
        pr.enable()

    run_command(args, log, catalog)

    if _PROFILE:
        pr.disable()
        pr.print_stats(sort='time')
        dt_str = beg_time.strftime("%Y%m%d-%H%M%S")
        profile_fname = "{:mod}_{:date}_cprofile-run-stats.dat".format(catalog_module_name, dt_str)
        msg = "Saved profile stats to '{}'".format(profile_fname)
        log.warning("")
        log.warning("="*len(msg))
        log.warning(msg)
        log.warning("="*len(msg))
        log.warning("")
        pr.dump_stats(profile_fname)

    end_time = datetime.now()
    log.warning("\nAll complete at {}".format(end_time))
    log.warning("Duration {}\n".format(end_time - beg_time))
    return


def load_log(args):
    """Load a `logging.Logger` object.

    Arguments
    ---------
    args : `argparse.Namespace` object
        Namespace containing required settings:
        {`args.debug`, `args.verbose`, and `args.log_filename`}.

    Returns
    -------
    log : `logging.Logger` object

    """

    # Determine verbosity ('None' means use default)
    log_stream_level = None
    if args.debug:
        log_stream_level = logger.DEBUG
    elif args.verbose:
        log_stream_level = logger.INFO

    # Create log
    log = logger.get_logger(stream_level=log_stream_level, tofile=args.log_filename)
    log._verbose = args.verbose
    log._debug = args.debug
    return log


def run_command(args, log, catalog):
    log.debug(__file__ + ":run_command()")
    log_lvl = log.INFO

    # Data Import
    # -----------
    if args.command == 'import':
        log.log(log_lvl, "Running 'import'")
        catalog.import_data()
        # importer = catalog.Importer(catalog)
        # importer.import_data()

    # Data Export
    # -----------
    elif args.subcommand == 'produce':
        # from . import production
        log.log(log_lvl, "Running 'produce'.")
        manager = catalog.Director(catalog, args)
        manager.direct(args)

    # Git Subcommands
    # ---------------
    elif args.subcommand.startswith('git'):
        from . import gitter

        if args.subcommand == 'git-clone':
            log.log(log_lvl, "Running 'git clone'.")
            gitter.git_clone_all_repos(catalog)
        elif args.subcommand == 'git-push':
            log.log(log_lvl, "Running 'git push'.")
            gitter.git_add_commit_push_all_repos(catalog)
        elif args.subcommand == 'git-pull':
            log.log(log_lvl, "Running 'git pull'.")
            gitter.git_pull_all_repos(catalog)
        elif args.subcommand == 'git-reset-local':
            log.log(log_lvl, "Running 'git reset' using the local HEAD.")
            gitter.git_reset_all_repos(catalog, hard=True, origin=False, clean=True)
        elif args.subcommand == 'git-reset-origin':
            log.log(log_lvl, "Running 'git reset' using 'origin/master'.")
            gitter.git_reset_all_repos(catalog, hard=True, origin=True, clean=True)
        elif args.subcommand == 'git-status':
            log.log(log_lvl, "Running 'git status'.")
            gitter.git_status_all_repos(catalog)
        else:
            log.error("Unrecognized git subcommand '{}'".format(args.subcommand))

    # Analyze Catalogs
    # ----------------
    elif args.subcommand == 'analyze':
        log.log(log_lvl, "Running 'analyze'.")
        from . import analysis
        # Create an `Analysis` instance
        lysis = analysis.analysis.Analysis(catalog, log)
        # Pass the command-line arguments to run.
        lysis.analyze(args)

    return


def setup(log):
    log.debug(__file__ + ":setup()")

    # Setup schema files
    # ------------------------
    log.info("Setting up schema")
    import astrocats.structures.schema
    astrocats.structures.schema.setup(log=log)

    return


def setup_catalog(catalog, git_clone=True):
    log = catalog.log
    log.debug(__file__ + ":setup_catalog()")

    # Setup git repositories
    # -------------------------
    if git_clone:
        log.info("Cloning all repos")
        gitter.git_clone_all_repos(catalog)

    return


if __name__ == "__main__":
    main()
