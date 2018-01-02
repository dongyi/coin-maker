"""

strategy trading engine
策略交易引擎

"""


def load_ipython_extension(ipython):
    pass


def run_file(strategy_file_path, config=None):
    from core.utils import parse_config
    from core.utils import clear_caches

    if config is None:
        config = {
            "base": {
                "strategy_file": strategy_file_path
            }
        }

    else:
        assert type(config) is dict
        if "base" in config:
            config["base"]["strategy_file"] = strategy_file_path
        else:
            config["base"] = {
                "strategy_file": strategy_file_path
            }
    config = parse_config(config)
    clear_caches()
    run(config)


def run(config):
    pass
